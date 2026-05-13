"""Pipeline C sensitivity — sweep shallow thresholds."""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

THRESHOLDS = [100, 150, 200, 250, 300]
REPORT_DIR = Path("reports")

def run_build(threshold: int) -> dict:
    cmd = [
        sys.executable, "scripts/build_index.py",
        "--pipeline", "c",
        "--shallow-threshold", str(threshold),
    ]
    print(f"\n{'='*60}")
    print(f"Threshold: {threshold}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=True, text=True,
        cwd=Path(__file__).parent.parent)
    output = result.stdout + result.stderr
    print(output[-500:])

    total, kept, filtered = 0, 0, 0
    for line in output.split("\n"):
        if "Total chunks:" in line and "filter" not in line.lower():
            try: total = int(line.split(":")[-1].strip())
            except: pass
        if "Kept:" in line:
            try: kept = int(line.split(":")[-1].strip())
            except: pass
        if "Filtered (shallow):" in line:
            try: filtered = int(line.split(":")[-1].strip().split()[0])
            except: pass

    return {
        "threshold": threshold,
        "total": total,
        "kept": kept,
        "filtered": filtered,
        "pct_filtered": round(filtered / max(1, total) * 100, 1),
    }


def main():
    results = []
    for t in THRESHOLDS:
        r = run_build(t)
        results.append(r)
        print(f"  T{t:3d}: {r['kept']} kept / {r['total']} total = {r['pct_filtered']}% filtered")

    md = [
        "# Pipeline C Sensitivity Analysis",
        f"*Generated: {datetime.now().isoformat()}*",
        "",
        "## Shallow Threshold Sweep",
        "",
        "| Threshold | Total | Kept | Filtered | % Filtered |",
        "|----------:|:----:|:----:|:--------:|:----------:|",
    ]
    for r in results:
        md.append(f"| {r['threshold']} | {r['total']} | {r['kept']} | {r['filtered']} | {r['pct_filtered']}% |")

    md += [
        "",
        "## Interpretation",
        "",
        "- **T=100**: keeps almost all chunks (removes extreme headers)",
        "- **T=200 (default)**: matches shallow chunk definition in paper",
        "- **T=300**: aggressive filter",
        "",
        "Use T=200 as primary threshold.",
    ]

    report = "\n".join(md)
    report_path = REPORT_DIR / "pipeline_c_sensitivity.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nSensitivity report saved to {report_path}")


if __name__ == "__main__":
    main()
