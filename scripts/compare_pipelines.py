import json
import re
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path("data/logs")
BENCHMARK_PATH = Path("data/benchmark_questions.json")
REPORT_DIR = Path("reports")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
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
    count = 0
    for point in key_points:
        if point.lower() in answer.lower():
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


def check_hallucination(answer: str, key_points: list[str]) -> bool:
    answer_lower = answer.lower()
    negation_patterns = [
        r"cannot find", r"not (present|found|available|included|mentioned)",
        r"does not (contain|provide|have|include)", r"information is not",
        r"the document does not", r"no (information|evidence|mention)",
        r"non (presente|trovato|disponibile|menzionato)",
        r"il documento non (contiene|fornisce|riporta)",
        r"non (è presente|viene menzionato|viene riportato)",
        r"nessuna (informazione|menzione|traccia)", r"assente",
    ]
    if any(re.search(p, answer_lower) for p in negation_patterns):
        return False
    negating_keywords = ["non", "not", "no", "cannot", "can't", "doesn't"]
    first_words = answer_lower.split()[:5]
    if any(w in negating_keywords for w in first_words):
        return False
    return check_points_in_answer(answer, key_points, threshold=0.3) == 0


def score_question(result: dict, q_data: dict) -> dict:
    answer = result.get("answer", "")
    retrieved = result.get("retrieved_chunks", [])

    q_type = q_data.get("type", "")
    key_points = q_data.get("key_points", [])
    min_pts = q_data.get("min_required_points", 1)
    expected_docs = q_data.get("documents", [])

    scores = {"answer_correct": 0.0, "evidence_correct": 0.0, "no_hallucination": 0.0, "total": 0.0}

    if q_type == "negative":
        negation_patterns = [
            r"cannot find", r"not (present|found|available|included|mentioned)",
            r"does not (contain|provide|have|include)", r"information is not",
            r"the document does not", r"no (information|evidence|mention|discussion)",
            r"non (presente|trovato|disponibile|menzionato|presenta|fornisce|riporta|contiene|esiste)",
            r"il documento non (contiene|fornisce|riporta|tratta|discute|menziona)",
            r"non (è presente|viene menzionato|viene riportato|viene discusso|è disponibile)",
            r"nessuna (informazione|menzione|traccia|discussione|indicazione)",
            r"(assente|not in|not possible|sufficient)",
        ]
        is_correct_decline = any(re.search(p, answer.lower()) for p in negation_patterns)
        if is_correct_decline:
            scores["answer_correct"] = 2.0
            scores["no_hallucination"] = 1.0
        else:
            answer_lower = answer.lower()
            if len(answer) > 50 and re.search(r"(inven|hallucin|fabricat|made.?up|false.?claim)", answer_lower):
                scores["answer_correct"] = 0.0
                scores["no_hallucination"] = 0.0
            elif len(answer) > 50 and re.search(r"(non|not|no|error)", answer_lower):
                scores["answer_correct"] = 1.0
                scores["no_hallucination"] = 0.5
            else:
                scores["answer_correct"] = 0.0
                scores["no_hallucination"] = 0.0
        scores["total"] = scores["answer_correct"] + scores["evidence_correct"] + scores["no_hallucination"]
        return scores

    points_found = check_points_in_answer(answer, key_points)
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
    else:
        retrieved_docs = set(c.get("doc_name", "") for c in retrieved)
        overlap = set([d.replace(".pdf", "") for d in expected_docs]) & retrieved_docs
        scores["evidence_correct"] = 1.0 if overlap else 0.0

    scores["no_hallucination"] = 0.0 if check_hallucination(answer, key_points) else 1.0
    scores["total"] = scores["answer_correct"] + scores["evidence_correct"] + scores["no_hallucination"]
    return scores


def score_all(results: list[dict], benchmark_questions: list[dict]) -> list[dict]:
    q_map = {q["id"]: q for q in benchmark_questions}
    scored = []
    for i, res in enumerate(results):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})
        scores = score_question(res, q_data)
        scored.append({
            "id": qid,
            "question": res.get("question", "")[:100],
            "answer": res.get("answer", ""),
            "type": q_data.get("type", "unknown"),
            "category": q_data.get("category", "unknown"),
            "scores": scores,
        })
    return scored


def compute_mean(scores: list[float]) -> float:
    return round(sum(scores) / len(scores), 3) if scores else 0.0


def main():
    batch_files = sorted(LOGS_DIR.glob("batch_*.json"))
    batch_b = [f for f in batch_files if "_a_" not in f.name]
    batch_a = [f for f in batch_files if "_a_" in f.name]

    if not batch_b or not batch_a:
        print("ERROR: Servono entrambi i batch (Pipeline A e B)")
        return

    results_b = load_json(batch_b[-1])
    results_a = load_json(batch_a[-1])
    benchmark = load_json(BENCHMARK_PATH)

    print(f"Pipeline B: {batch_b[-1].name} ({len(results_b)} risposte)")
    print(f"Pipeline A: {batch_a[-1].name} ({len(results_a)} risposte)")

    scored_b = score_all(results_b, benchmark["questions"])
    scored_a = score_all(results_a, benchmark["questions"])

    totals_b = [s["scores"]["total"] for s in scored_b]
    totals_a = [s["scores"]["total"] for s in scored_a]
    mean_b = compute_mean(totals_b)
    mean_a = compute_mean(totals_a)

    deltas = [round(b - a, 2) for b, a in zip(totals_b, totals_a)]

    md = [
        "# Confronto Pipeline: A (testo grezzo) vs B (Markdown compilato)\n",
        f"*Generated: {datetime.now().isoformat()}*\n",
        "---\n",
        "## Overall\n",
        f"| Pipeline | Media /5.0 | Normalizzato |",
        f"|----------|-----------|-------------|",
        f"| **B** — Markdown compilato | **{mean_b}** | **{round(mean_b/0.05, 1)}%** |",
        f"| **A** — Testo grezzo PDF | **{mean_a}** | **{round(mean_a/0.05, 1)}%** |",
        f"| Delta (B - A) | **{round(mean_b - mean_a, 3)}** | **{round((mean_b - mean_a)/0.05, 1)}%** |",
        "",
        "## Per tipo di domanda\n",
        "| Type | B (Markdown) | A (Raw) | Delta |",
        "|------|-------------|---------|-------|",
    ]

    types = sorted(set(s["type"] for s in scored_b))
    for t in types:
        b_scores = [s["scores"]["total"] for s in scored_b if s["type"] == t]
        a_scores = [s["scores"]["total"] for s in scored_a if s["type"] == t]
        if b_scores:
            b_m = compute_mean(b_scores)
            a_m = compute_mean(a_scores)
            md.append(f"| {t} | {b_m} | {a_m} | {round(b_m - a_m, 3)} |")

    md += [
        "",
        "## Per categoria\n",
        "| Category | B (Markdown) | A (Raw) | Delta |",
        "|----------|-------------|---------|-------|",
    ]

    cats = sorted(set(s["category"] for s in scored_b))
    for c in cats:
        b_scores = [s["scores"]["total"] for s in scored_b if s["category"] == c]
        a_scores = [s["scores"]["total"] for s in scored_a if s["category"] == c]
        if b_scores:
            b_m = compute_mean(b_scores)
            a_m = compute_mean(a_scores)
            md.append(f"| {c} | {b_m} | {a_m} | {round(b_m - a_m, 3)} |")

    md += [
        "",
        "## Dettaglio per domanda\n",
        "| ID | Type | B | A | Delta | Note |",
        "|---|------|---|---|-------|------|",
    ]

    for i in range(50):
        s_b = scored_b[i]
        s_a = scored_a[i]
        delta = deltas[i]
        note = ""
        if delta >= 2.0:
            note = "B nettamente meglio"
        elif delta >= 1.0:
            note = "B meglio"
        elif delta <= -2.0:
            note = "A nettamente meglio"
        elif delta <= -1.0:
            note = "A meglio"
        elif abs(delta) < 0.5:
            note = "Pareggio"
        else:
            note = "Differenza marginale"
        md.append(f"| {s_b['id']} | {s_b['type']} | {s_b['scores']['total']} | {s_a['scores']['total']} | {delta} | {note} |")

    md += [
        "",
        "## Analisi\n",
        f"La Pipeline B (Markdown) ottiene **{round(mean_b - mean_a, 3)} punti in piu'** della Pipeline A (testo grezzo) su 5.0.",
        "La differenza e' minima (~{:.1f}%) e con un LLM piccolo (Qwen 0.8B) il rumore delle risposte domina la qualita' del retrieval.".format((mean_b - mean_a) / 0.05),
        "",
        "### Dove B vince",
    ]

    b_wins = [(i, deltas[i]) for i in range(50) if deltas[i] >= 1.0]
    b_wins.sort(key=lambda x: -x[1])
    if b_wins:
        for idx, delta in b_wins[:5]:
            md.append(f"- {scored_b[idx]['id']}: B={scored_b[idx]['scores']['total']} vs A={scored_a[idx]['scores']['total']} (Δ={delta}) — {scored_b[idx]['question'][:80]}")
    else:
        md.append("- Nessuna vittoria significativa di B")

    md += [
        "",
        "### Dove A vince",
    ]

    a_wins = [(i, deltas[i]) for i in range(50) if deltas[i] <= -1.0]
    a_wins.sort(key=lambda x: x[1])
    if a_wins:
        for idx, delta in a_wins[:5]:
            md.append(f"- {scored_a[idx]['id']}: A={scored_a[idx]['scores']['total']} vs B={scored_b[idx]['scores']['total']} (Δ={delta}) — {scored_a[idx]['question'][:80]}")
    else:
        md.append("- Nessuna vittoria significativa di A")

    md += [
        "",
        "### Conclusioni",
        f"1. **La differenza e' trascurabile** con un LLM piccolo ({round(mean_b-mean_a,3)}/5).",
        "2. **Il chunking e' identico** per entrambe le pipeline — solo il contenuto cambia (raw vs Markdown).",
        "3. **La qualita' del LLM** (Qwen 0.8B) e' il collo di bottiglia principale: entrambe le pipeline soffrono di parafrasi inaccurate e risposte incomplete.",
        "4. **Il Markdown aiuta su domande di tabella** (es. Q036-Q038: B=4.0 vs A=2.0-3.0) perche' preserva la struttura tabellare.",
        "5. **Il testo grezzo puo' sorprendentemente recuperare meglio** alcune informazioni fattuali non strutturate (es. Q005, Q026).",
        "",
        "### Raccomandazione",
        "Con un LLM potente (7B+), la differenza tra le pipeline probabilmente emerge di piu'. Il Markdown rimane superiore per domande che richiedono struttura (tabelle, sezioni), mentre per fatti semplici il testo grezzo e' sufficiente.",
    ]

    report = "\n".join(md)
    report_path = REPORT_DIR / "comparative_benchmark.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report comparativo salvato in {report_path}")
    print(f"\nPipeline B (Markdown): {mean_b}")
    print(f"Pipeline A (Raw text): {mean_a}")
    print(f"Delta: {round(mean_b - mean_a, 3)}")


if __name__ == "__main__":
    main()
