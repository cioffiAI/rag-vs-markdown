"""Batch runner for Gemma 3 4B (Ollama Cloud) — runs all 3 pipelines."""
import subprocess
import sys
from pathlib import Path

BENCHMARK_FILE = "data/benchmark_questions.json"

PIPELINES = [
    {"pipeline": "a", "tag": "gemma4b_a"},
    {"pipeline": "b", "tag": "gemma4b_b"},
    {"pipeline": "c", "tag": "gemma4b_c"},
]

MODEL = "gemma3:4b-cloud"
PROVIDER = "ollama"
MAX_TOKENS = 256

def main():
    print(f"Gemma 3 4B — All Pipelines (A/B/C) via Ollama Cloud")
    print(f"Benchmark: {BENCHMARK_FILE}")
    print(f"Model: {MODEL}, Provider: {PROVIDER}")
    print()

    for p in PIPELINES:
        print(f"\n=== Pipeline {p['pipeline'].upper()} ({p['tag']}) ===")
        cmd = [
            sys.executable, "scripts/query.py",
            "--pipeline", p["pipeline"],
            "--file", BENCHMARK_FILE,
            "--model", MODEL,
            "--provider", PROVIDER,
            "--tag", p["tag"],
            "--max-tokens", str(MAX_TOKENS),
        ]
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        if result.returncode != 0:
            print(f"WARNING: {p['tag']} returned code {result.returncode}")

    print(f"\nAll 3 pipelines completed!")
    print(f"Generate report: python scripts/compare_pipelines.py --pipelines a,b,c --batch-a <log_a> --batch-b <log_b> --batch-c <log_c>")

if __name__ == "__main__":
    main()
