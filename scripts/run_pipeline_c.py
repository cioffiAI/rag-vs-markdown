"""Batch runner for Pipeline C — runs all available models."""
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BENCHMARK_FILE = "data/benchmark_questions.json"

MODELS = [
    {"model": "gemma3:4b-cloud", "provider": "ollama", "tag": "c_gemma4b", "max_tokens": 256},
    {"model": "nemotron-3-super-free", "provider": "opencode-zen", "tag": "c_nemotron", "max_tokens": 256},
    {"model": "deepseek-v4-flash", "provider": "opencode-go", "tag": "c_deepseek", "max_tokens": 1024},
    {"model": "gemma-4-26b-a4b-it", "provider": "gemini", "tag": "c_gemma", "max_tokens": 256},
]

def main():
    print("Pipeline C — Batch query runner")
    print(f"Benchmark: {BENCHMARK_FILE}")
    print()

    for m in MODELS:
        print(f"\n--- {m['tag']} ---")
        cmd = [
            sys.executable, "scripts/query.py",
            "--pipeline", "c",
            "--file", BENCHMARK_FILE,
            "--model", m["model"],
            "--provider", m["provider"],
            "--tag", m["tag"],
            "--max-tokens", str(m["max_tokens"]),
        ]
        result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
        if result.returncode != 0:
            print(f"WARNING: {m['tag']} returned code {result.returncode}")

    print(f"\nBatch Pipeline C completed!")
    print("Generate report: python scripts/compare_pipelines.py --pipelines a,b,c")

if __name__ == "__main__":
    main()
