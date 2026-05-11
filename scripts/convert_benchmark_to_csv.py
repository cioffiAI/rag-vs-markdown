import json
import csv
from pathlib import Path

BENCHMARK_PATH = Path("data/benchmark_questions.json")
CSV_PATH = Path("data/gold_questions.csv")

def main():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    questions = data["questions"]
    rows = []
    for q in questions:
        rows.append({
            "id": q["id"],
            "type": q["type"],
            "category": q["category"],
            "documents": ";".join(q.get("documents", [])),
            "question": q["question"],
            "expected_answer": q.get("expected_answer", ""),
            "key_points": ";".join(q.get("key_points", [])),
            "min_required_points": q.get("min_required_points", 1),
            "answerable": str(q.get("answerable", True)),
        })

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV creato: {CSV_PATH} ({len(rows)} domande)")

if __name__ == "__main__":
    main()
