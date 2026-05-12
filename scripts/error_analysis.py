import json
import re
from pathlib import Path

LOGS_DIR = Path("data/logs")
REPORT_DIR = Path("reports")
BENCHMARK_PATH = Path("data/benchmark_questions.json")

NEGATION_PATTERNS = [
    r"cannot find",
    r"not (present|found|available|included|mentioned)",
    r"does not (contain|provide|have|include)",
    r"information is not",
    r"the document does not",
    r"no (information|evidence|mention|discussion)",
    r"non (presente|trovato|disponibile|menzionato|presenta|fornisce|riporta|contiene|esiste)",
    r"il documento non (contiene|fornisce|riporta|tratta|discute|menziona)",
    r"non (è presente|viene menzionato|viene riportato|viene discusso|è disponibile)",
    r"nessuna (informazione|menzione|traccia|discussione|indicazione)",
    r"(assente|not in|not possible|sufficient)",
]


def load_benchmark():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_results(path: str) -> list[dict]:
    p = Path(path)
    if p.is_absolute():
        full_path = p
    else:
        full_path = LOGS_DIR / path
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r'\w+', text.lower()))


def _word_overlap(answer_words: set[str], point: str) -> float:
    point_words = _tokenize(point)
    if not point_words:
        return 0.0
    overlap = len(answer_words & point_words)
    return overlap / len(point_words)


def is_negation_answer(answer: str) -> bool:
    return any(re.search(p, answer.lower()) for p in NEGATION_PATTERNS)


def is_llm_error(answer: str) -> bool:
    return answer.startswith("[ERROR LLM:")


def classify_error(result: dict, benchmark_q: dict) -> list[str]:
    answer = result.get("answer", "")
    retrieved_chunks = result.get("retrieved_chunks", [])
    expected_docs = benchmark_q.get("documents", [])
    q_type = benchmark_q.get("type", "")

    if is_llm_error(answer):
        return ["LLM_ERROR"]

    retrieved_doc_names = set()
    for c in retrieved_chunks:
        name = c.get("doc_name", "")
        retrieved_doc_names.add(name)

    expected_doc_stems = set()
    for d in expected_docs:
        stem = d.replace(".pdf", "")
        expected_doc_stems.add(stem)

    correct_doc_in_chunks = bool(retrieved_doc_names & expected_doc_stems)

    if q_type == "negative":
        if is_negation_answer(answer):
            return ["CORRECT_REFUSAL"]
        return ["E05"]

    primary = []
    secondary = []

    if not correct_doc_in_chunks:
        primary.append("E01")
        if not is_negation_answer(answer):
            secondary.append("E05")
        return primary + (["+" + s for s in secondary] if secondary else [])

    is_decline = is_negation_answer(answer)
    if is_decline:
        primary.append("E06")
        return primary

    # Check hallucination: answer has content but no key points match
    key_points = benchmark_q.get("key_points", [])
    expected_answer = benchmark_q.get("expected_answer", "")
    answer_lower = answer.lower()

    FIRST_WORD_NEGATION = ["non", "not", "no", "cannot", "can't", "doesn't"]
    first_words = answer_lower.split()[:5]
    starts_negation = any(w in FIRST_WORD_NEGATION for w in first_words) or \
                      any(re.search(p, answer_lower) for p in NEGATION_PATTERNS)

    if not starts_negation and key_points:
        answer_words = _tokenize(answer)
        points_found = 0
        for point in key_points:
            if point.lower() in answer_lower:
                points_found += 1
            elif _word_overlap(answer_words, point) >= 0.3:
                points_found += 1
        if points_found == 0 and len(answer) > 20:
            primary.append("E05")
            return primary

    # Check citation
    has_citation = False
    answer_lc = answer.lower()
    for doc_name in expected_docs:
        stem = doc_name.replace(".pdf", "").replace("_", " ").lower()
        if stem in answer_lc:
            has_citation = True
            break
    if not has_citation:
        secondary.append("E04")

    # Check context ignored: correct doc retrieved, not declined, answer is poor
    if key_points:
        answer_words = _tokenize(answer)
        points_found = 0
        for point in key_points:
            if point.lower() in answer_lower:
                points_found += 1
            elif _word_overlap(answer_words, point) >= 0.3:
                points_found += 1
        min_pts = benchmark_q.get("min_required_points", 1)
        if points_found < min_pts:
            primary.append("E03")
        else:
            if not has_citation:
                primary.append("E04")
    else:
        primary.append("E07")

    result_codes = primary[:1]
    if secondary:
        result_codes.append("+" + secondary[0])
    return result_codes if result_codes else ["E07"]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Classifica errori usando la tassonomia E01-E07")
    parser.add_argument("batch_file", type=str, nargs="?",
                        help="File batch retrieval (in data/logs/ o percorso assoluto)")
    parser.add_argument("--oracle", type=str, default="",
                        help="File batch oracle per confronto (opzionale)")
    parser.add_argument("--output", type=str, default="",
                        help="Nome del report output (in reports/)")
    parser.add_argument("--pipeline-label", type=str, default="",
                        help="Etichetta pipeline per il report")
    parser.add_argument("--model-label", type=str, default="",
                        help="Etichetta modello per il report")
    args = parser.parse_args()

    # Auto-select latest batch if none specified
    batch_path = args.batch_file or sorted(LOGS_DIR.glob("batch_*.json"))[-1].name
    results = load_results(batch_path)
    benchmark = load_benchmark()
    q_map = {q["id"]: q for q in benchmark["questions"]}

    oracle_results = []
    if args.oracle:
        oracle_results = load_results(args.oracle)

    pipeline_label = args.pipeline_label or "?"
    model_label = args.model_label or "?"

    print(f"Analisi errori per: {batch_path}")
    print(f"Pipeline: {pipeline_label}, Modello: {model_label}")
    print(f"Domande: {len(results)}")

    error_counts = {f"E0{i}": 0 for i in range(1, 8)}
    error_counts["LLM_ERROR"] = 0
    error_counts["CORRECT_REFUSAL"] = 0
    error_counts["CORRECT"] = 0
    error_type_dist = {}
    detailed = []

    for i, res in enumerate(results):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})
        codes = classify_error(res, q_data)

        # Collect score info
        retrieved = res.get("retrieved_chunks", [])
        correct_docs = set(d.replace(".pdf", "") for d in q_data.get("documents", []))
        retrieved_doc_names = set(c.get("doc_name", "") for c in retrieved)
        doc_retrieved = bool(retrieved_doc_names & correct_docs)

        answer_preview = res.get("answer", "")[:120]

        entry = {
            "id": qid,
            "type": q_data.get("type", "?"),
            "category": q_data.get("category", "?"),
            "question": res.get("question", "")[:80],
            "answer_preview": answer_preview,
            "codes": codes,
            "doc_retrieved": doc_retrieved,
        }
        detailed.append(entry)

        q_type = q_data.get("type", "unknown")
        if q_type not in error_type_dist:
            error_type_dist[q_type] = {"count": 0, "errors": {}}

        error_type_dist[q_type]["count"] += 1

        main_code = codes[0] if codes else "E07"
        if main_code == "CORRECT_REFUSAL" or (main_code == "E07" and q_data.get("type") != "negative"):
            pass  # Count these below

        if main_code in error_counts:
            error_counts[main_code] += 1
        else:
            error_counts[main_code] = 1

        if main_code not in error_type_dist[q_type]["errors"]:
            error_type_dist[q_type]["errors"][main_code] = 0
        error_type_dist[q_type]["errors"][main_code] += 1

        if main_code not in ("LLM_ERROR",):
            print(f"  {qid}: {codes} | doc_ok={doc_retrieved} | {q_data.get('type', '?'):15s} | {res.get('question', '')[:60]}...")

    # Summary
    print("\n" + "=" * 60)
    print(f"PROFILO ERRORI — {pipeline_label} / {model_label}")
    print("=" * 60)
    print(f"{'Codice':12s} {'Nome':22s} {'Conteggio':>8s}")
    print("-" * 42)
    tax_map = {
        "E01": "retrieval_miss",
        "E02": "retrieval_weak",
        "E03": "context_ignored",
        "E04": "citation_missing",
        "E05": "hallucination",
        "E06": "false_refusal",
        "E07": "scoring_fuzzy",
    }
    for code, name in tax_map.items():
        count = error_counts.get(code, 0)
        bar = "#" * (count // 2) if count > 0 else ""
        print(f"{code:12s} {name:22s} {count:>4d}  {bar}")
    print(f"{'CORRECT_REF':12s} {'correct refusal':22s} {error_counts.get('CORRECT_REFUSAL', 0):>4d}")
    print(f"{'LLM_ERROR':12s} {'LLM error':22s} {error_counts.get('LLM_ERROR', 0):>4d}")

    # Error profile table
    print("\n\nPer-Type Error Profile:")
    print(f"{'Type':22s} {'Count':>6s} {'E01':>4s} {'E03':>4s} {'E04':>4s} {'E05':>4s} {'E06':>4s} {'E07':>4s} {'REF':>4s}")
    print("-" * 62)
    for qtype, dist in sorted(error_type_dist.items()):
        e = dist["errors"]
        print(f"{qtype:22s} {dist['count']:>6d} {e.get('E01', 0):>4d} {e.get('E03', 0):>4d} {e.get('E04', 0):>4d} {e.get('E05', 0):>4d} {e.get('E06', 0):>4d} {e.get('E07', 0):>4d} {e.get('CORRECT_REFUSAL', 0):>4d}")

    total_with_errors = sum(error_counts.get(c, 0) for c in tax_map)
    retrieval_errors = error_counts.get("E01", 0)
    generation_errors = sum(error_counts.get(c, 0) for c in ["E03", "E04", "E05", "E06"])

    print(f"\nRETRIEVAL ERRORS (E01):      {retrieval_errors}/{len(results)} ({100*retrieval_errors//len(results)}%)")
    print(f"GENERATION ERRORS (E03-E06): {generation_errors}/{len(results)} ({100*generation_errors//len(results)}%)")
    print(f"CORRECT REFUSALS:             {error_counts.get('CORRECT_REFUSAL', 0)}/{len(results)}")

    # Save report
    report_name = args.output or f"error_profile_{pipeline_label}_{model_label}.md"
    report_path = REPORT_DIR / report_name
    lines = [
        f"# Error Profile: {pipeline_label} / {model_label}",
        f"",
        f"**Batch file:** {batch_path}",
        f"**Oracle file:** {args.oracle or 'N/A'}",
        f"**Questions:** {len(results)}",
        f"",
        f"## Error Counts",
        f"",
        f"| Code | Name | Count |",
        f"|------|------|-------|",
    ]
    for code, name in tax_map.items():
        lines.append(f"| {code} | {name} | {error_counts.get(code, 0)} |")
    lines += [
        f"| CORRECT_REFUSAL | correct refusal (negative) | {error_counts.get('CORRECT_REFUSAL', 0)} |",
        f"| LLM_ERROR | LLM error | {error_counts.get('LLM_ERROR', 0)} |",
        f"",
        f"**Retrieval errors (E01):** {retrieval_errors}/{len(results)}",
        f"**Generation errors (E03-E06):** {generation_errors}/{len(results)}",
        f"**Correct refusals:** {error_counts.get('CORRECT_REFUSAL', 0)}/{len(results)}",
        f"",
        f"## Per-Type Error Profile",
        f"",
        f"| Type | Count | E01 | E03 | E04 | E05 | E06 | E07 | REF |",
        f"|------|-------|-----|-----|-----|-----|-----|-----|-----|",
    ]
    for qtype, dist in sorted(error_type_dist.items()):
        e = dist["errors"]
        lines.append(f"| {qtype} | {dist['count']} | {e.get('E01', 0)} | {e.get('E03', 0)} | {e.get('E04', 0)} | {e.get('E05', 0)} | {e.get('E06', 0)} | {e.get('E07', 0)} | {e.get('CORRECT_REFUSAL', 0)} |")

    lines += [
        f"",
        f"## Per-Question Classification",
        f"",
        f"| ID | Type | Doc OK | Codes | Answer Preview |",
        f"|----|------|--------|-------|----------------|",
    ]
    for d in detailed:
        lines.append(f"| {d['id']} | {d['type']} | {d['doc_retrieved']} | {','.join(d['codes'])} | {d['answer_preview'][:60].replace('|', '/')} |")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport salvato: {report_path}")


if __name__ == "__main__":
    main()
