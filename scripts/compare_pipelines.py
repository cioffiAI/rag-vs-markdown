import argparse
import json
import re
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path("data/logs")
BENCHMARK_PATH = Path("data/benchmark_questions.json")
REPORT_DIR = Path("reports")
PIPELINE_NAMES = {"a": "Raw", "b": "Markdown", "c": "MD-filtered"}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r'\w+', text.lower()))


def _word_overlap(answer_words: set[str], point: str) -> float:
    point_words = _tokenize(point)
    return len(answer_words & point_words) / len(point_words) if point_words else 0.0


def check_points_in_answer(answer: str, key_points: list[str], threshold: float = 0.4) -> int:
    answer_words = _tokenize(answer)
    count = 0
    for point in key_points:
        if point.lower() in answer.lower() or _word_overlap(answer_words, point) >= threshold:
            count += 1
    return count


def check_document_citation(answer: str, expected_docs: list[str]) -> bool:
    answer_lower = answer.lower()
    for doc_name in expected_docs:
        if doc_name.replace(".pdf", "").replace("_", " ").lower() in answer_lower:
            return True
    return False


def check_hallucination(answer: str, key_points: list[str]) -> bool:
    answer_lower = answer.lower()
    negation_patterns = [
        r"cannot find", r"not (present|found|available)", r"does not (contain|provide|have|include)",
        r"information is not", r"the document does not", r"no (information|evidence|mention)",
        r"non (presente|trovato|disponibile|menzionato)", r"il documento non (contiene|fornisce|riporta)",
        r"non (è presente|viene menzionato)", r"nessuna (informazione|menzione|traccia)", r"assente",
    ]
    if any(re.search(p, answer_lower) for p in negation_patterns):
        return False
    negating_keywords = ["non", "not", "no", "cannot", "can't", "doesn't"]
    if any(w in negating_keywords for w in answer_lower.split()[:5]):
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
        negs = [r"cannot find", r"not (present|found|available|included|mentioned)",
                r"does not (contain|provide|have|include)", r"information is not",
                r"the document does not", r"no (information|evidence|mention|discussion)",
                r"non (presente|trovato|disponibile|menzionato|presenta|fornisce|riporta|contiene|esiste)",
                r"il documento non", r"non (è presente|viene menzionato|viene riportato)",
                r"nessuna (informazione|menzione|traccia|discussione|indicazione)",
                r"(assente|not in|not possible|sufficient)"]
        if any(re.search(p, answer.lower()) for p in negs):
            scores["answer_correct"] = 2.0
            scores["no_hallucination"] = 1.0
        else:
            answer_lower = answer.lower()
            if len(answer) > 50 and re.search(r"(inven|hallucin|fabricat|made.?up|false.?claim)", answer_lower):
                scores["answer_correct"] = 0.0; scores["no_hallucination"] = 0.0
            elif len(answer) > 50 and re.search(r"(non|not|no|error)", answer_lower):
                scores["answer_correct"] = 1.0; scores["no_hallucination"] = 0.5
            else:
                scores["answer_correct"] = 0.0; scores["no_hallucination"] = 0.0
        scores["total"] = scores["answer_correct"] + scores["evidence_correct"] + scores["no_hallucination"]
        return scores

    points_found = check_points_in_answer(answer, key_points)
    answer_ratio = min(1.0, points_found / max(1, min_pts))
    if answer_ratio >= 1.0: scores["answer_correct"] = 2.0
    elif answer_ratio >= 0.5: scores["answer_correct"] = 1.0
    else: scores["answer_correct"] = 0.5 if points_found > 0 else 0.0

    has_citation = check_document_citation(answer, expected_docs)
    if has_citation: scores["evidence_correct"] = 2.0
    else:
        retrieved_docs = set(c.get("doc_name", "") for c in retrieved)
        overlap = set(d.replace(".pdf", "") for d in expected_docs) & retrieved_docs
        scores["evidence_correct"] = 1.0 if overlap else 0.0

    scores["no_hallucination"] = 0.0 if check_hallucination(answer, key_points) else 1.0
    scores["total"] = scores["answer_correct"] + scores["evidence_correct"] + scores["no_hallucination"]
    return scores


def score_all(results, benchmark_questions):
    q_map = {q["id"]: q for q in benchmark_questions}
    scored = []
    for i, res in enumerate(results):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})
        s = score_question(res, q_data)
        scored.append({"id": qid, "type": q_data.get("type", "unknown"), "scores": s})
    return scored


def compute_mean(scores):
    return round(sum(scores) / len(scores), 3) if scores else 0.0


def find_latest_batch(pipeline: str) -> Path:
    pattern = f"batch_{pipeline}_"
    candidates = sorted(LOGS_DIR.glob(f"{pattern}*.json"))
    if not candidates:
        candidates = sorted(LOGS_DIR.glob(f"batch_*{pipeline}*.json"))
    return candidates[-1] if candidates else None


def main():
    parser = argparse.ArgumentParser(description="Compare RAG pipelines")
    parser.add_argument("--pipelines", type=str, default="a,b")
    parser.add_argument("--batch-a", type=str, default="")
    parser.add_argument("--batch-b", type=str, default="")
    parser.add_argument("--batch-c", type=str, default="")
    parser.add_argument("--output", type=str, default="")
    args = parser.parse_args()

    pipeline_list = [p.strip() for p in args.pipelines.split(",")]
    batch_map = {"a": args.batch_a, "b": args.batch_b, "c": args.batch_c}
    benchmark = load_json(BENCHMARK_PATH)
    results = {}
    batch_files = {}

    for p in pipeline_list:
        if p not in ("a", "b", "c"):
            print(f"ERROR: pipeline '{p}' unknown")
            return
        bpath = LOGS_DIR / batch_map[p] if batch_map[p] else find_latest_batch(p)
        if not bpath or not bpath.exists():
            print(f"ERROR: batch for {p.upper()} not found. Use --batch-{p}")
            return
        results[p] = score_all(load_json(bpath), benchmark["questions"])
        batch_files[p] = bpath.name
        print(f"Pipeline {p.upper()} ({PIPELINE_NAMES[p]}): {len(results[p])} answers from {bpath.name}")

    totals = {p: [s["scores"]["total"] for s in results[p]] for p in pipeline_list}
    means = {p: compute_mean(totals[p]) for p in pipeline_list}

    output_name = args.output or f"comparative_{'_'.join(pipeline_list)}.md"
    baseline = pipeline_list[0]
    n = len(pipeline_list)

    md = [
        f"# Confronto: {' vs '.join(PIPELINE_NAMES[p] for p in pipeline_list)}",
        f"*Generated: {datetime.now().isoformat()}*",
        "",
        "## Overall",
        "",
        "| Model/Config | " + " | ".join(f"{PIPELINE_NAMES[p]}" for p in pipeline_list),
    ]
    header2 = "|" + "---|" + ":---:|" * n + "|"
    md.append(header2)
    row = "| Overall | " + " | ".join(f"**{means[p]}**" for p in pipeline_list) + " |"
    md.append(row)
    md.append("")

    if n >= 2:
        md.append("## Deltas")
        md.append("")
        md.append("| Comparison | Delta | % |")
        md.append("|------------|:-----:|:-:|")
        for j in range(1, n):
            d = round(means[pipeline_list[j]] - means[baseline], 3)
            pct = round(d / 0.05, 1)
            md.append(f"| {PIPELINE_NAMES[pipeline_list[j]]} - {PIPELINE_NAMES[baseline]} | {d} | {pct}% |")
        md.append("")

    types = sorted(set(s["type"] for s in results[pipeline_list[0]]))
    md.append("## Per tipo di domanda")
    md.append("")
    md.append("| Type | " + " | ".join(f"{PIPELINE_NAMES[p]}" for p in pipeline_list) + " |")
    md.append("|------|" + ":---:|" * n + "|")
    for t in types:
        trow = f"| {t} |"
        for p in pipeline_list:
            ts = [s["scores"]["total"] for s in results[p] if s["type"] == t]
            trow += f" {compute_mean(ts) if ts else 0.0:.2f} |"
        md.append(trow)

    report = "\n".join(md)
    report_path = REPORT_DIR / output_name
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport saved to {report_path}")


if __name__ == "__main__":
    main()
