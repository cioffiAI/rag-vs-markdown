"""Bootstrap + permutation test per paired pipeline comparisons."""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from evaluate import score_question

BENCHMARK_PATH = Path("data/benchmark_questions.json")
REPORT_DIR = Path("reports")
DEFAULT_N_RESAMPLES = 10000
SEED = 42

MODELS_CONFIG = [
    {
        "name": "Gemma 3 4B",
        "size": "4B",
        "batches": {
            "a": "data/logs/batch_gemma4b_a_20260513_145110.json",
            "b": "data/logs/batch_gemma4b_b_20260513_145234.json",
            "c": "data/logs/batch_gemma4b_c_20260513_145354.json",
        },
    },
    {
        "name": "Nemotron 3",
        "size": "~3B",
        "batches": {
            "a": "data/logs/batch_a_20260512_154147.json",
            "b": "data/logs/batch_b_20260512_155538.json",
            "c": "data/logs/batch_c_nemotron_20260513_133527.json",
        },
    },
    {
        "name": "DeepSeek V4 Flash",
        "size": "—",
        "batches": {
            "a": "data/logs/batch_a_20260512_162048.json",
            "b": "data/logs/batch_b_20260512_163557.json",
            "c": "data/logs/batch_c_deepseek_20260513_133529.json",
        },
    },
    {
        "name": "Gemma 4 26B",
        "size": "26B",
        "batches": {
            "a": "data/logs/batch_gemma26b_a_20260512_122008.json",
            "b": "data/logs/batch_gemma26b_b_merged.json",
            "c": "data/logs/batch_c_gemma_20260513_112953.json",
            "c_retry": "data/logs/batch_c_gemma_20260513_115440.json",
        },
        "unreliable_c": True,
    },
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_benchmark():
    return load_json(BENCHMARK_PATH)["questions"]


def build_q_map(benchmark):
    return {q["question"].strip(): q for q in benchmark}


def align_questions(batch_a, batch_b, q_map):
    """Match questions by text between two batch files. Returns aligned pairs."""
    q_map_b = {r["question"].strip(): r for r in batch_b}
    pairs = []
    unmatched = 0
    for ra in batch_a:
        q_text = ra["question"].strip()
        rb = q_map_b.get(q_text)
        if rb is None:
            unmatched += 1
            continue
        q_data = q_map.get(q_text, {})
        pairs.append((ra, rb, q_data))
    if unmatched > 0:
        print(f"  Warning: {unmatched} questions in A not matched in B")
    return pairs


def compute_paired_deltas(batch_a, batch_b, q_map):
    """Compute delta_i = score_A_i - score_B_i for each matched question."""
    pairs = align_questions(batch_a, batch_b, q_map)
    deltas = []
    per_type = defaultdict(list)
    for ra, rb, q_data in pairs:
        sa = score_question(ra, q_data)["total"]
        sb = score_question(rb, q_data)["total"]
        delta = sa - sb
        deltas.append(delta)
        q_type = q_data.get("type", "unknown")
        per_type[q_type].append(delta)
    return np.array(deltas), dict(per_type)


def bootstrap_ci(deltas, n_resamples=DEFAULT_N_RESAMPLES, ci=95, seed=SEED):
    """Bootstrap confidence interval for the mean of paired deltas."""
    rng = np.random.default_rng(seed)
    n = len(deltas)
    means = np.array([
        np.mean(rng.choice(deltas, size=n, replace=True))
        for _ in range(n_resamples)
    ])
    low = np.percentile(means, (100 - ci) / 2)
    high = np.percentile(means, 100 - (100 - ci) / 2)
    return np.mean(deltas), low, high


def permutation_test(deltas, n_perm=DEFAULT_N_RESAMPLES, seed=SEED):
    """Permutation test for paired deltas. H0: mean(delta) = 0."""
    rng = np.random.default_rng(seed)
    observed = np.mean(deltas)
    count = 0
    for _ in range(n_perm):
        signs = rng.choice([-1, 1], size=len(deltas))
        perm_mean = np.mean(deltas * signs)
        if abs(perm_mean) >= abs(observed):
            count += 1
    p_value = (count + 1) / (n_perm + 1)
    return p_value


def format_ci(low, high):
    return f"[{low:+.2f}, {high:+.2f}]"


def analyze(model_cfg, pipeline_x, pipeline_y, n_resamples=DEFAULT_N_RESAMPLES):
    """Run bootstrap + permutation for one model, one pipeline pair."""
    batch_x = load_json(model_cfg["batches"][pipeline_x])
    batch_y = load_json(model_cfg["batches"][pipeline_y])
    q_map = build_q_map(load_benchmark())

    deltas, per_type = compute_paired_deltas(batch_x, batch_y, q_map)
    n = len(deltas)
    mean_delta = np.mean(deltas)
    _, ci_low, ci_high = bootstrap_ci(deltas, n_resamples=n_resamples)
    p_val = permutation_test(deltas, n_perm=n_resamples)

    result = {
        "n": n,
        "mean": mean_delta,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "p_value": p_val,
        "per_type": {},
    }

    PIPELINE_LABELS = {"a": "Raw", "b": "Markdown", "c": "MD-filtered"}
    xl = PIPELINE_LABELS.get(pipeline_x, pipeline_x)
    yl = PIPELINE_LABELS.get(pipeline_y, pipeline_y)
    print(f"  {xl} vs {yl}: "
          f"n={n} delta={mean_delta:+.2f} CI={format_ci(ci_low, ci_high)} p={p_val:.3f}")

    for q_type, d in per_type.items():
        d = np.array(d)
        m = np.mean(d)
        _, cl, ch = bootstrap_ci(d, n_resamples=n_resamples)
        p = permutation_test(d, n_perm=n_resamples)
        result["per_type"][q_type] = {
            "n": len(d),
            "mean": m,
            "ci_low": cl,
            "ci_high": ch,
            "p_value": p,
        }
        print(f"    {q_type} (n={len(d)}): delta={m:+.2f} CI={format_ci(cl, ch)} p={p:.3f}")

    return result


def generate_report(all_results, output_path, n_resamples):
    PIPELINE_LABELS = {"a": "Raw", "b": "Markdown", "c": "MD-filtered"}
    comparisons = [("a", "b", "Raw-MD"), ("a", "c", "Raw-MDf"), ("b", "c", "MD-MDf")]

    lines = [
        "# Bootstrap & Permutation Test Results",
        "",
        f"*Generated: {datetime.now().isoformat()}*",
        f"*Resamples: {n_resamples} | Seed: {SEED} | CI: 95%*",
        "",
    ]

    for px, py, label in comparisons:
        lines += [
            f"## {PIPELINE_LABELS[px]} vs {PIPELINE_LABELS[py]}  (\u0394 {label})",
            "",
            f"| Model | Size | \u0394 {label} | CI 95% | p-value | n |",
            f"|-------|------|:-------:|:------:|:-------:|:-:|",
        ]
        for m in all_results:
            r = m.get(f"{px}_vs_{py}")
            if r is None:
                lines.append(f"| {m['name']} | {m['size']} | — | — | — | — |")
                continue
            warning = " \u2020" if m.get("unreliable_c") and py == "c" else ""
            lines.append(
                f"| {m['name']}{warning} | {m['size']} | "
                f"{r['mean']:+.2f} | "
                f"{format_ci(r['ci_low'], r['ci_high'])} | "
                f"{r['p_value']:.3f} | "
                f"{r['n']} |"
            )
        lines.append("")

        if any(m.get("unreliable_c") and py == "c" for m in all_results):
            lines.append(
                "\u2020 Gemma 4 26B Pipeline C affected by Gemini API 500 errors "
                "(18/50 questions). Results diagnostic only."
            )
            lines.append("")

    lines += [
        "---",
        "",
        "## Per-Question Type Breakdown",
        "",
    ]

    for px, py, label in comparisons:
        lines += [
            f"### {PIPELINE_LABELS[px]} vs {PIPELINE_LABELS[py]}",
            "",
        ]
        for m in all_results:
            r = m.get(f"{px}_vs_{py}")
            if r is None or not r.get("per_type"):
                continue
            lines.append(f"#### {m['name']} ({m['size']})")
            lines.append("")
            lines.append("| Type | n | \u0394 | CI 95% | p-value |")
            lines.append("|------|:-:|:---:|:------:|:-------:|")
            for q_type in ["simple", "local_reasoning", "multi_document",
                            "table_extraction", "negative"]:
                pt = r["per_type"].get(q_type)
                if pt:
                    lines.append(
                        f"| {q_type} | {pt['n']} | {pt['mean']:+.2f} | "
                        f"{format_ci(pt['ci_low'], pt['ci_high'])} | "
                        f"{pt['p_value']:.3f} |"
                    )
            lines.append("")

    lines += [
        "---",
        "",
        "## Caveats",
        "",
        "- **Per-type analysis is diagnostic (5-15 examples per type), not "
        "statistically robust.** Small sample sizes inflate confidence intervals "
        "and reduce power.",
        "- **Gemma 4 26B Pipeline C** affected by Gemini API HTTP 500 errors "
        "(36% of questions). Results marked with \u2020 are unreliable for this "
        "model-pipeline.",
        "- **Bootstrap assumes i.i.d. residuals.** With 50 questions, the paired "
        "bootstrap on deltas is the appropriate non-parametric method.",
        "- **Permutation test** tests H\u2080: mean(\u0394) = 0 via label "
        "randomization within each question pair.",
        "- **Scoring method**: fuzzy word-overlap (threshold 0.4), same as "
        "`evaluate.py`. Same scoring function used for all pipelines.",
        "",
        "## Interpretation Guide",
        "",
        "- **\u0394 > 0**: Pipeline X scores higher than Pipeline Y "
        "(Raw advantage, or filter recovery)",
        "- **p < 0.05**: Statistically significant at conventional threshold",
        "- **CI excludes 0**: Directional effect supported at 95% confidence",
        "- **Small per-type groups (e.g., table_metric: n=5)**: Interpret with "
        "extreme caution",
    ]

    report = "\n".join(lines)
    output_dir = Path(output_path).parent
    output_dir.mkdir(exist_ok=True)
    Path(output_path).write_text(report, encoding="utf-8")
    print(f"\nReport saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap + permutation test for paired pipeline deltas"
    )
    parser.add_argument(
        "--model", type=str, default="",
        help="Run single model by name"
    )
    parser.add_argument(
        "--batch-a", type=str, default="",
        help="Override Pipeline A batch file"
    )
    parser.add_argument(
        "--batch-b", type=str, default="",
        help="Override Pipeline B batch file"
    )
    parser.add_argument(
        "--batch-c", type=str, default="",
        help="Override Pipeline C batch file"
    )
    parser.add_argument(
        "--n-resamples", type=int, default=DEFAULT_N_RESAMPLES,
        help=f"Number of bootstrap/permutation resamples (default: {DEFAULT_N_RESAMPLES})"
    )
    parser.add_argument(
        "--output", type=str, default="reports/bootstrap_results.md",
        help="Output report path"
    )
    args = parser.parse_args()

    models = MODELS_CONFIG
    if args.model:
        models = [m for m in MODELS_CONFIG if m["name"] == args.model]
        if not models:
            print(f"Unknown model: {args.model}")
            print(f"Available: {[m['name'] for m in MODELS_CONFIG]}")
            sys.exit(1)

    all_results = []
    for mc in models:
        name = mc["name"]
        batches = dict(mc["batches"])
        if args.batch_a:
            batches["a"] = args.batch_a
        if args.batch_b:
            batches["b"] = args.batch_b
        if args.batch_c:
            batches["c"] = args.batch_c

        print(f"\n{'='*60}")
        print(f"Model: {name} ({mc['size']})")
        print(f"{'='*60}")

        model_result = {"name": name, "size": mc["size"]}
        if mc.get("unreliable_c"):
            model_result["unreliable_c"] = True
            print("  Note: Pipeline C marked as unreliable (Gemini API errors)")

        for px, py in [("a", "b"), ("a", "c"), ("b", "c")]:
            if px not in batches or py not in batches:
                continue
            key = f"{px}_vs_{py}"
            try:
                model_result[key] = analyze(mc, px, py, n_resamples=args.n_resamples)
            except Exception as e:
                print(f"  ERROR in {px} vs {py}: {e}")
                model_result[key] = None

        all_results.append(model_result)

    generate_report(all_results, args.output, args.n_resamples)


if __name__ == "__main__":
    main()
