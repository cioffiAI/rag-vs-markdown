import json
import re
from pathlib import Path

LOGS_DIR = Path("data/logs")
BENCHMARK_PATH = Path("data/benchmark_questions.json")
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def load_benchmark() -> dict:
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def load_results(batch_file: str = None) -> list[dict]:
    if batch_file:
        path = LOGS_DIR / batch_file
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    log_files = sorted(LOGS_DIR.glob("batch_*.json"))
    if not log_files:
        raise FileNotFoundError("Nessun batch log trovato in data/logs/")
    with open(log_files[-1], "r", encoding="utf-8") as f:
        return json.load(f)

def _tokenize(text: str) -> set[str]:
    return set(re.findall(r'\w+', text.lower()))

def _word_overlap(answer_words: set[str], point: str) -> float:
    point_words = _tokenize(point)
    if not point_words:
        return 0.0
    overlap = len(answer_words & point_words)
    return overlap / len(point_words)

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
    """Check if the answer references the correct source document."""
    answer_lower = answer.lower()
    for doc_name in expected_docs:
        stem = doc_name.replace(".pdf", "").replace("_", " ").lower()
        if stem in answer_lower:
            return True
    return False

def check_hallucination(answer: str, key_points: list[str], expected_answer: str) -> bool:
    answer_lower = answer.lower()
    negation_patterns = [
        r"cannot find",
        r"not (present|found|available|included|mentioned)",
        r"does not (contain|provide|have|include)",
        r"information is not",
        r"the document does not",
        r"no (information|evidence|mention)",
        r"non (presente|trovato|disponibile|menzionato)",
        r"il documento non (contiene|fornisce|riporta)",
        r"non (è presente|viene menzionato|viene riportato)",
        r"nessuna (informazione|menzione|traccia)",
        r"assente",
    ]
    is_negation = any(re.search(p, answer_lower) for p in negation_patterns)
    if is_negation:
        return False

    negating_keywords = ["non", "not", "no", "cannot", "can't", "doesn't"]
    first_words = answer_lower.split()[:5]
    if any(w in negating_keywords for w in first_words):
        return False

    points = check_points_in_answer(answer, key_points, threshold=0.3)
    return points == 0

def score_question(result: dict, benchmark_q: dict) -> dict:
    question_text = result.get("question", "")
    answer = result.get("answer", "")
    retrieved = result.get("retrieved_chunks", [])

    q_type = benchmark_q.get("type", "")
    q_category = benchmark_q.get("category", "")
    answerable = benchmark_q.get("answerable", True)
    key_points = benchmark_q.get("key_points", [])
    expected_answer = benchmark_q.get("expected_answer", "")
    min_pts = benchmark_q.get("min_required_points", 1)
    expected_docs = benchmark_q.get("documents", [])
    acceptable = benchmark_q.get("acceptable_behavior", "")

    scores = {
        "answer_correct": 0.0,
        "evidence_correct": 0.0,
        "no_hallucination": 0.0,
        "total": 0.0,
    }

    if q_type == "negative":
        negation_patterns = [
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
    min_for_correct = min_pts
    answer_ratio = min(1.0, points_found / max(1, min_for_correct))
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
        if overlap:
            scores["evidence_correct"] = 1.0
        else:
            scores["evidence_correct"] = 0.0

    is_hallucinated = check_hallucination(answer, key_points, expected_answer)
    if not is_hallucinated:
        scores["no_hallucination"] = 1.0
    else:
        scores["no_hallucination"] = 0.0

    scores["total"] = scores["answer_correct"] + scores["evidence_correct"] + scores["no_hallucination"]
    return scores

def compute_summary(results: list[dict], benchmark: dict) -> dict:
    q_map = {q["id"]: q for q in benchmark["questions"]}

    per_type = {}
    per_category = {}
    all_totals = []

    for i, res in enumerate(results):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})
        scores = score_question(res, q_data)
        total = scores["total"]

        q_type = q_data.get("type", "unknown")
        q_cat = q_data.get("category", "unknown")

        per_type.setdefault(q_type, []).append(total)
        per_category.setdefault(q_cat, []).append(total)
        all_totals.append(total)

    summary = {
        "total_questions": len(all_totals),
        "mean_score": round(sum(all_totals) / len(all_totals), 2),
        "max_possible": 5.0,
        "by_type": {k: {
            "count": len(v),
            "mean": round(sum(v) / len(v), 2),
            "min": round(min(v), 2),
            "max": round(max(v), 2),
        } for k, v in sorted(per_type.items())},
        "by_category": {k: {
            "count": len(v),
            "mean": round(sum(v) / len(v), 2),
        } for k, v in sorted(per_category.items())},
        "detailed_scores": [round(t, 2) for t in all_totals],
    }

    return summary

def generate_report(summary: dict, batch_file: str = None) -> str:
    md = [
        "# RAG Benchmark Evaluation Report\n",
        f"*Generated: {__import__('datetime').datetime.now().isoformat()}*\n",
        f"*Batch file: {batch_file or 'latest'}*\n",
        "---\n",
        "## Overall Results\n",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Questions | {summary['total_questions']} |",
        f"| Mean Score (max 5) | {summary['mean_score']} |",
        f"| Normalized (%) | {round(summary['mean_score'] / 0.05, 1)}% |",
        "",
        "## Results by Question Type\n",
        "| Type | Count | Mean | Min | Max |",
        "|------|-------|------|-----|-----|",
    ]

    for qtype, stats in summary["by_type"].items():
        md.append(f"| {qtype} | {stats['count']} | {stats['mean']} | {stats['min']} | {stats['max']} |")

    md += [
        "",
        "## Results by Category\n",
        "| Category | Count | Mean |",
        "|----------|-------|------|",
    ]
    for cat, stats in summary["by_category"].items():
        md.append(f"| {cat} | {stats['count']} | {stats['mean']} |")

    md += [
        "",
        "## Detailed Scores\n",
        f"```\n{summary['detailed_scores']}\n```",
    ]

    return "\n".join(md)

def main(batch_file: str = None, output_report: str = "benchmark_results.md"):
    benchmark = load_benchmark()
    results = load_results(batch_file)

    print(f"Valutazione di {len(results)} risposte...")
    q_map = {q["id"]: q for q in benchmark["questions"]}

    detailed = []
    for i, res in enumerate(results):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})
        scores = score_question(res, q_data)
        detailed.append({
            "id": qid,
            "question": res.get("question", "")[:80],
            "answer_preview": res.get("answer", "")[:100],
            "scores": scores,
        })
        print(f"  {qid}: {scores['total']:.1f}/5.0  (answer={scores['answer_correct']}, evidence={scores['evidence_correct']}, no_halluc={scores['no_hallucination']})")

    summary = compute_summary(results, benchmark)
    print(f"\nMedia: {summary['mean_score']:.2f}/5.0")

    report_md = generate_report(summary, batch_file)
    report_path = REPORT_DIR / output_report
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"\nReport salvato: {report_path}")

    summary_path = REPORT_DIR / "benchmark_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": summary,
            "detailed": detailed,
        }, f, ensure_ascii=False, indent=2)
    print(f"Summary JSON salvato: {summary_path}")

if __name__ == "__main__":
    import sys
    batch = sys.argv[1] if len(sys.argv) > 1 else None
    report_name = sys.argv[2] if len(sys.argv) > 2 else "benchmark_results.md"
    main(batch, report_name)
