import json
import re
from pathlib import Path

LOGS_DIR = Path("data/logs")
REPORT_DIR = Path("reports")
BENCHMARK_PATH = Path("data/benchmark_questions.json")

NEGATION_PATTERNS = [
    r"cannot find", r"not (present|found|available|included|mentioned)",
    r"does not (contain|provide|have|include)", r"information is not",
    r"the document does not", r"no (information|evidence|mention|discussion)",
    r"non (presente|trovato|disponibile|menzionato|presenta|fornisce|riporta|contiene|esiste)",
    r"il documento non (contiene|fornisce|riporta|tratta|discute|menziona)",
    r"non (e' presente|viene menzionato|viene riportato|viene discusso|e' disponibile)",
    r"nessuna (informazione|menzione|traccia|discussione|indicazione)",
    r"(assente|not in|not possible|sufficient)",
]


def load_benchmark():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r'\w+', text.lower()))


def _word_overlap(answer_words: set[str], point: str) -> float:
    point_words = _tokenize(point)
    if not point_words:
        return 0.0
    return len(answer_words & point_words) / len(point_words)


def check_points_in_answer(answer: str, key_points: list[str], threshold: float = 0.4) -> int:
    answer_words = _tokenize(answer)
    answer_lower = answer.lower()
    count = 0
    for point in key_points:
        if point.lower() in answer_lower:
            count += 1
        elif _word_overlap(answer_words, point) >= threshold:
            count += 1
    return count


def check_document_citation(answer: str, expected_docs: list[str]) -> bool:
    answer_lower = answer.lower()
    for doc_name in expected_docs:
        stem = doc_name.replace(".pdf", "").replace("_", " ").lower()
        if stem in answer_lower:
            return True
    return False


def score_answer(answer: str, benchmark_q: dict, retrieved_chunks: list[dict] = None) -> dict:
    q_type = benchmark_q.get("type", "")
    key_points = benchmark_q.get("key_points", [])
    min_pts = benchmark_q.get("min_required_points", 1)
    expected_docs = benchmark_q.get("documents", [])

    scores = {"answer_correct": 0.0, "evidence_correct": 0.0, "no_hallucination": 0.0, "total": 0.0}

    if q_type == "negative":
        is_correct_decline = any(re.search(p, answer.lower()) for p in NEGATION_PATTERNS)
        if is_correct_decline:
            scores["answer_correct"] = 2.0
            scores["no_hallucination"] = 1.0
        elif len(answer) > 50 and re.search(r"(non|not|no|error)", answer.lower()):
            scores["answer_correct"] = 1.0
            scores["no_hallucination"] = 0.5
        scores["total"] = scores["answer_correct"] + scores["evidence_correct"] + scores["no_hallucination"]
        return scores

    answer_lower = answer.lower()
    is_negation = any(re.search(p, answer_lower) for p in NEGATION_PATTERNS)

    if is_negation:
        scores["answer_correct"] = 0.0
        scores["evidence_correct"] = 0.0
        scores["no_hallucination"] = 1.0
        scores["total"] = 1.0
        return scores

    points_found = check_points_in_answer(answer, key_points, threshold=0.3)
    answer_ratio = min(1.0, points_found / max(1, min_pts))
    if answer_ratio >= 1.0:
        scores["answer_correct"] = 2.0
    elif answer_ratio >= 0.5:
        scores["answer_correct"] = 1.0
    else:
        scores["answer_correct"] = 0.5 if points_found > 0 else 0.0

    has_citation = check_document_citation(answer, expected_docs)
    if has_citation:
        scores["evidence_correct"] = 2.0
    elif retrieved_chunks:
        retrieved_docs = set(c.get("doc_name", "") for c in retrieved_chunks)
        expected_stems = set(d.replace(".pdf", "") for d in expected_docs)
        if retrieved_docs & expected_stems:
            scores["evidence_correct"] = 1.0
    scores["no_hallucination"] = 1.0
    scores["total"] = scores["answer_correct"] + scores["evidence_correct"] + scores["no_hallucination"]
    return scores


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Confronta punteggi retrieval vs oracle")
    parser.add_argument("retrieval_batch", type=str, help="File batch retrieval (in data/logs/)")
    parser.add_argument("oracle_batch", type=str, help="File batch oracle (in data/logs/)")
    parser.add_argument("--pipeline-label", type=str, default="?", help="Label pipeline")
    parser.add_argument("--model-label", type=str, default="?", help="Label modello")
    args = parser.parse_args()

    with open(LOGS_DIR / args.retrieval_batch, "r", encoding="utf-8") as f:
        retrieval_results = json.load(f)
    with open(LOGS_DIR / args.oracle_batch, "r", encoding="utf-8") as f:
        oracle_results = json.load(f)

    benchmark = load_benchmark()
    q_map = {q["id"]: q for q in benchmark["questions"]}

    retrieval_scores = []
    oracle_scores = []
    comparison = []

    for i in range(min(len(retrieval_results), len(oracle_results), 50)):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})

        r_res = retrieval_results[i]
        o_res = oracle_results[i]

        r_s = score_answer(r_res["answer"], q_data, r_res.get("retrieved_chunks"))
        o_s = score_answer(o_res["answer"], q_data, r_res.get("retrieved_chunks"))

        retrieval_scores.append(r_s["total"])
        oracle_scores.append(o_s["total"])

        delta = o_s["total"] - r_s["total"]
        comparison.append({
            "id": qid,
            "type": q_data.get("type", "?"),
            "retrieval_score": r_s["total"],
            "oracle_score": o_s["total"],
            "delta": round(delta, 1),
            "retrieval_q_preview": r_res.get("answer", "")[:80],
            "oracle_q_preview": o_res.get("answer", "")[:80],
        })

    # Summary
    r_mean = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0
    o_mean = sum(oracle_scores) / len(oracle_scores) if oracle_scores else 0
    avg_delta = o_mean - r_mean

    print(f"Confronto: {args.retrieval_batch} vs {args.oracle_batch}")
    print(f"Domande confrontate: {len(comparison)}")
    print(f"\nPunteggi medi:")
    print(f"  Retrieval: {r_mean:.2f}/5.0")
    print(f"  Oracle:    {o_mean:.2f}/5.0")
    print(f"  Delta:     {avg_delta:+.2f}/5.0")
    print(f"  Miglioramento oracle: {abs(avg_delta/r_mean*100):.1f}%" if avg_delta > 0 else f"  Peggioramento: {abs(avg_delta/r_mean*100):.1f}%")

    # Per-type breakdown
    from collections import defaultdict
    type_r = defaultdict(list)
    type_o = defaultdict(list)
    for c in comparison:
        type_r[c["type"]].append(c["retrieval_score"])
        type_o[c["type"]].append(c["oracle_score"])

    print(f"\nPer-type breakdown:")
    print(f"{'Type':20s} {'Retrieval':>10s} {'Oracle':>10s} {'Delta':>8s}")
    print("-" * 50)
    for qtype in sorted(type_r.keys()):
        r_avg = sum(type_r[qtype]) / len(type_r[qtype])
        o_avg = sum(type_o[qtype]) / len(type_o[qtype])
        print(f"{qtype:20s} {r_avg:>8.2f}   {o_avg:>8.2f}   {o_avg-r_avg:>+6.2f}")

    # Per-question detail
    print(f"\nPer-question delta (oracle - retrieval):")
    for c in comparison:
        arrow = " +" if c["delta"] > 0 else (" =" if c["delta"] == 0 else " ")
        print(f"  {c['id']} ({c['type']:15s}): {c['retrieval_score']:.1f} -> {c['oracle_score']:.1f} [{arrow}{c['delta']:+.1f}]")

    # Generate report
    labels = f"{args.pipeline_label}_{args.model_label}" if args.pipeline_label != "?" else "comparison"
    report_path = REPORT_DIR / f"oracle_comparison_{labels}.md"
    lines = [
        f"# Oracle Comparison: {args.pipeline_label} / {args.model_label}",
        f"",
        f"**Retrieval batch:** {args.retrieval_batch}",
        f"**Oracle batch:** {args.oracle_batch}",
        f"**Questions compared:** {len(comparison)}",
        f"",
        f"## Overall",
        f"",
        f"| Metric | Retrieval | Oracle | Delta |",
        f"|--------|-----------|--------|-------|",
        f"| Mean score | {r_mean:.2f} | {o_mean:.2f} | {avg_delta:+.2f} |",
        f"| Improvement | — | — | {abs(avg_delta/r_mean*100):.1f}% |",
        f"",
        f"## By Type",
        f"",
        f"| Type | Retrieval | Oracle | Delta |",
        f"|------|-----------|--------|-------|",
    ]
    for qtype in sorted(type_r.keys()):
        r_avg = sum(type_r[qtype]) / len(type_r[qtype])
        o_avg = sum(type_o[qtype]) / len(type_o[qtype])
        lines.append(f"| {qtype} | {r_avg:.2f} | {o_avg:.2f} | {o_avg-r_avg:+.2f} |")

    lines += [
        f"",
        f"## Per-Question",
        f"",
        f"| ID | Type | Retrieval | Oracle | Delta |",
        f"|----|------|-----------|--------|-------|",
    ]
    for c in comparison:
        lines.append(f"| {c['id']} | {c['type']} | {c['retrieval_score']:.1f} | {c['oracle_score']:.1f} | {c['delta']:+.1f} |")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nReport salvato: {report_path}")


if __name__ == "__main__":
    main()
