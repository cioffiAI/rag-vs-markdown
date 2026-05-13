"""Compare LLM judge scores vs fuzzy overlap scores per pipeline."""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from evaluate import score_question

LOGS_DIR = Path("data/logs")
BENCHMARK_PATH = Path("data/benchmark_questions.json")
REPORT_DIR = Path("reports")

PIPELINE_LABELS = {"a": "Raw", "b": "Markdown", "c": "MD-filtered"}

MODEL_BATCHES = [
    {
        "name": "Gemma 3 4B",
        "size": "4B",
        "batches": {
            "a": ("data/logs/batch_gemma4b_a_20260513_145110.json", "data/logs/judge_gemma4b_a.json"),
            "b": ("data/logs/batch_gemma4b_b_20260513_145234.json", "data/logs/judge_gemma4b_b.json"),
            "c": ("data/logs/batch_gemma4b_c_20260513_145354.json", "data/logs/judge_gemma4b_c.json"),
        },
    },
    {
        "name": "Nemotron 3",
        "size": "~3B",
        "batches": {
            "a": ("data/logs/batch_a_20260512_154147.json", "data/logs/judge_nemotron3_a.json"),
            "b": ("data/logs/batch_b_20260512_155538.json", "data/logs/judge_nemotron3_b.json"),
            "c": ("data/logs/batch_c_nemotron_20260513_133527.json", "data/logs/judge_nemotron3_c.json"),
        },
    },
    {
        "name": "DeepSeek V4 Flash",
        "size": "—",
        "batches": {
            "a": ("data/logs/batch_a_20260512_162048.json", "data/logs/judge_deepseek_a.json"),
            "b": ("data/logs/batch_b_20260512_163557.json", "data/logs/judge_deepseek_b.json"),
            "c": ("data/logs/batch_c_deepseek_20260513_133529.json", "data/logs/judge_deepseek_c.json"),
        },
    },
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_fuzzy_scores(batch, benchmark_questions):
    q_map = {q["id"]: q for q in benchmark_questions}
    scores = []
    for i, entry in enumerate(batch):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})
        s = score_question(entry, q_data)
        scores.append({"id": qid, "type": q_data.get("type", "unknown"), "total": s["total"]})
    return scores


def compute_judge_scores(judge_path):
    if not judge_path.exists():
        return None
    data = load_json(judge_path)
    scores = []
    for s in data["scores"]:
        scores.append({
            "id": s["question_id"],
            "type": s["type"],
            "score": s["score"],
        })
    return scores


def pearson_corr(x, y):
    if len(x) < 3:
        return None
    r = np.corrcoef(x, y)[0, 1]
    if np.isnan(r):
        return None
    return round(r, 4)


def spearman_corr(x, y):
    if len(x) < 3:
        return None
    from scipy.stats import spearmanr
    r, _ = spearmanr(x, y)
    if np.isnan(r):
        return None
    return round(r, 4)


def align_scores(fuzzy, judge):
    fuzzy_map = {s["id"]: s for s in fuzzy}
    pairs = []
    for js in judge:
        fs = fuzzy_map.get(js["id"])
        if fs is not None and js["score"] is not None:
            pairs.append((fs["total"], js["score"], js["id"], js["type"]))
    return pairs


def mean(values):
    return sum(values) / len(values) if values else 0.0


def per_type_breakdown(pairs):
    by_type = defaultdict(list)
    for f, j, qid, qtype in pairs:
        by_type[qtype].append((f, j))
    return dict(by_type)


def generate_report(all_results):
    lines = [
        "# LLM Judge vs Fuzzy Overlap — Confronto",
        "",
        f"*Generated: {datetime.now().isoformat()}*",
        "",
        "## Metodologia",
        "",
        "- **Fuzzy overlap**: word-overlap (threshold 0.4) su key_points + "
        "document citation check + hallucination detection (scala 0-5).",
        "- **LLM judge**: nemotron-3-super:cloud via Ollama, rubrica 0-5, "
        "temperature=0.",
        "- **Correlazione**: Pearson e Spearman tra fuzzy_total e judge_score.",
        "",
        "---",
        "",
    ]

    for mc in all_results:
        name = mc["name"]
        lines.append(f"## {name} ({mc['size']})")
        lines.append("")

        for pipeline in ["a", "b", "c"]:
            results = mc.get(pipeline)
            if not results:
                continue

            pairs = results["pairs"]
            fuzzy_scores = [p[0] for p in pairs]
            judge_scores = [p[1] for p in pairs]

            if not pairs:
                lines.append(f"### Pipeline {PIPELINE_LABELS[pipeline]} ({pipeline.upper()})")
                lines.append("")
                lines.append("*Nessun dato.*")
                lines.append("")
                continue

            lines.append(f"### Pipeline {PIPELINE_LABELS[pipeline]} ({pipeline.upper()})")
            lines.append("")
            lines.append(f"| Metrica | Valore |")
            lines.append(f"|---------|-------:|")
            lines.append(f"| N | {len(pairs)} |")
            lines.append(f"| Fuzzy mean | {mean(fuzzy_scores):.2f} / 5.0 |")
            lines.append(f"| LLM judge mean | {mean(judge_scores):.2f} / 5.0 |")
            lines.append(f"| Delta (Judge − Fuzzy) | {results['delta_mean']:+.2f} |")
            lines.append(f"| Pearson r | {results['pearson']} |" if results.get("pearson") else "| Pearson r | — |")
            lines.append(f"| Spearman rho | {results['spearman']} |" if results.get("spearman") else "| Spearman rho | — |")

            by_type = results["per_type"]
            if by_type:
                lines.append("")
                lines.append("#### Per-type breakdown")
                lines.append("")
                lines.append("| Type | N | Fuzzy mean | Judge mean | Delta |")
                lines.append("|------|:-:|:----------:|:----------:|:-:|")
                for qtype in ["simple", "local_reasoning", "multi_document",
                              "table_extraction", "negative"]:
                    bt = by_type.get(qtype)
                    if bt and bt["n"] > 0:
                        lines.append(
                            f"| {qtype} | {bt['n']} | "
                            f"{bt['fuzzy_mean']:.2f} | "
                            f"{bt['judge_mean']:.2f} | "
                            f"{bt['delta']:+.2f} |"
                        )
            lines.append("")

    lines += [
        "---",
        "",
        "## Discrepanze annotate",
        "",
        "- **Negative questions**: fuzzy overlap tends to score negative "
        "questions highly (correct decline = 3.0), but LLM judge may penalize "
        "answers that do not explicitly state 'not in the document'.",
        "- **Table extraction**: fuzzy overlap may miss numerical precision "
        "while LLM judge evaluates correctness more holistically.",
        "- **Multi-document**: LLM judge can verify cross-document synthesis "
        "better than word overlap, which only checks per-document key points.",
        "",
        "## Limitazioni",
        "",
        "- LLM judge uses nemotron-3-super:cloud, not a dedicated evaluator model.",
        "- Judge prompt and rubric may introduce bias toward certain answer styles.",
        "- Small sample size per type (3-15 questions).",
    ]

    report = "\n".join(lines)
    report_path = REPORT_DIR / "llm_judge_results.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report salvato: {report_path}")


def main():
    benchmark = load_json(BENCHMARK_PATH)
    benchmark_questions = benchmark["questions"]

    all_results = []

    for mc in MODEL_BATCHES:
        name = mc["name"]
        print(f"\n{'='*60}")
        print(f"Model: {name}")
        print(f"{'='*60}")

        model_result = {"name": name, "size": mc["size"]}

        for pipeline in ["a", "b", "c"]:
            batch_path, judge_path = mc["batches"].get(pipeline, (None, None))
            if batch_path is None:
                print(f"  Pipeline {pipeline.upper()}: not configured — skipping")
                continue
            batch_path = Path(batch_path)
            judge_path = Path(judge_path)
            if not batch_path.exists():
                print(f"  Pipeline {pipeline.upper()}: batch not found — skipping")
                continue

            batch = load_json(batch_path)
            fuzzy_scores = compute_fuzzy_scores(batch, benchmark_questions)
            judge_scores = compute_judge_scores(judge_path)

            if judge_scores is None:
                print(f"  Pipeline {pipeline.upper()}: judge scores not found at {judge_path.name} — skipping")
                continue

            pairs = align_scores(fuzzy_scores, judge_scores)
            if not pairs:
                print(f"  Pipeline {pipeline.upper()}: no aligned pairs")
                continue

            fuzzy_vals = [p[0] for p in pairs]
            judge_vals = [p[1] for p in pairs]
            deltas = [j - f for f, j in zip(fuzzy_vals, judge_vals)]

            result = {
                "n": len(pairs),
                "fuzzy_mean": round(mean(fuzzy_vals), 3),
                "judge_mean": round(mean(judge_vals), 3),
                "delta_mean": round(mean(deltas), 3),
                "pairs": pairs,
                "per_type": {},
            }

            pearson = pearson_corr(fuzzy_vals, judge_vals)
            spearman = spearman_corr(fuzzy_vals, judge_vals)
            if pearson is not None:
                result["pearson"] = pearson
            if spearman is not None:
                result["spearman"] = spearman

            by_type = per_type_breakdown(pairs)
            for qtype, type_pairs in by_type.items():
                tf = [p[0] for p in type_pairs]
                tj = [p[1] for p in type_pairs]
                result["per_type"][qtype] = {
                    "n": len(tf),
                    "fuzzy_mean": round(mean(tf), 3),
                    "judge_mean": round(mean(tj), 3),
                    "delta": round(mean(tj) - mean(tf), 3),
                }

            model_result[pipeline] = result
            print(f"  Pipeline {pipeline.upper()}: n={result['n']} "
                  f"fuzzy={result['fuzzy_mean']:.2f} judge={result['judge_mean']:.2f} "
                  f"Delta={result['delta_mean']:+.2f} "
                  f"r={result.get('pearson', 'N/A')} "
                  f"rho={result.get('spearman', 'N/A')}")

        all_results.append(model_result)

    generate_report(all_results)


if __name__ == "__main__":
    main()
