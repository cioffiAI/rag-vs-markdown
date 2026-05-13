"""LLM-as-judge per RAG answer quality.
Usa nemotron-3-super:cloud via Ollama (localhost:11434/v1).
Rubrica 0-5, temperature=0, output solo numero.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from openai import OpenAI

JUDGE_MODEL = "nemotron-3-super:cloud"
JUDGE_PROVIDER = "ollama"
JUDGE_URL = "http://localhost:11434/v1"

BENCHMARK_PATH = Path("data/benchmark_questions.json")

JUDGE_PROMPT_TEMPLATE = """You are an expert evaluator of RAG (Retrieval-Augmented Generation) systems. Assess the quality of the answer based on the provided context and ground truth.

## Scoring Rubric (0-5)

- **0**: Completely wrong answer or hallucination — the answer fabricates information not present in the context, or contradicts the ground truth entirely.
- **1**: Minimal partial answer — only vaguely related to the question, most key facts are missing or incorrect.
- **2**: Partial answer — some correct facts present, but significant omissions (more than half of key points missing).
- **3**: Correct answer but NO source citation — the answer is factually correct but does not cite the source document.
- **4**: Correct answer with partial citation — answer is correct and references a source, but the citation is vague or incomplete.
- **5**: Complete, precise answer with explicit correct document citation — all key points covered, answer is accurate, and the correct source document is clearly cited.

## Context (retrieved chunks):
{context}

## Question:
{question}

## Ground Truth / Expected Answer:
{ground_truth}

## Generated Answer:
{answer}

## Output format:
Score: <number 0-5>
Reasoning: <brief explanation>"""


def load_benchmark(path: Path = BENCHMARK_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_question_map(benchmark: dict) -> dict:
    q_map = {}
    for q in benchmark["questions"]:
        q_map[q["id"]] = q
    return q_map


def build_context(chunks: list[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks):
        doc_name = c.get("doc_name", "unknown")
        text = c.get("text", "")
        parts.append(f"[Document {i+1}: {doc_name}]\n{text[:1500]}")
    return "\n\n".join(parts)


def build_prompt(question: str, answer: str, chunks: list[dict], ground_truth: str) -> str:
    context = build_context(chunks)
    return JUDGE_PROMPT_TEMPLATE.format(
        context=context,
        question=question,
        ground_truth=ground_truth,
        answer=answer,
    )


def call_judge(prompt: str, client: OpenAI) -> str:
    try:
        resp = client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=4096,
            timeout=180,
        )
        content = resp.choices[0].message.content or ""
        return content.strip()
    except Exception as e:
        return f"[ERROR: {e}]"


def parse_score(response: str) -> int | None:
    m = re.search(r"Score:\s*([0-5])", response, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"(?:score|rating|rate|valutazione)[:\s]*([0-5])", response, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m = re.search(r"\b([0-5])\b(?:\s*/\s*5)?", response)
    if m:
        return int(m.group(1))
    return None


def score_entry(entry: dict, q_data: dict, client: OpenAI) -> dict:
    question = entry.get("question", "")
    answer = entry.get("answer", "")
    chunks = entry.get("retrieved_chunks", [])
    ground_truth = q_data.get("expected_answer", "")

    prompt = build_prompt(question, answer, chunks, ground_truth)
    response = call_judge(prompt, client)
    score = parse_score(response)

    return {
        "question_id": q_data.get("id", "unknown"),
        "question": question[:120],
        "type": q_data.get("type", "unknown"),
        "score": score,
        "raw_response": response[:300],
        "ground_truth": ground_truth[:150],
    }


def safe_print(msg: str):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def main():
    parser = argparse.ArgumentParser(description="LLM-as-judge per RAG answer quality")
    parser.add_argument("--batch-file", type=str, required=True, help="Batch log JSON file")
    parser.add_argument("--output", type=str, default="", help="Output JSON file path")
    parser.add_argument("--max-samples", type=int, default=0, help="Number of samples to score (0 = all)")
    args = parser.parse_args()

    batch_path = Path(args.batch_file)
    if not batch_path.exists():
        safe_print(f"ERROR: batch file not found: {batch_path}")
        sys.exit(1)

    results = json.loads(batch_path.read_text(encoding="utf-8"))
    benchmark = load_benchmark()
    q_map = build_question_map(benchmark)

    client = OpenAI(base_url=JUDGE_URL, api_key="not-needed")
    safe_print(f"Judge model: {JUDGE_MODEL} via Ollama ({JUDGE_URL})")
    safe_print(f"Batch: {batch_path.name} ({len(results)} entries)")

    samples = results[:args.max_samples] if args.max_samples > 0 else results
    scores = []

    for i, entry in enumerate(samples):
        qid = f"Q{i+1:03d}"
        q_data = q_map.get(qid, {})
        if not q_data:
            safe_print(f"  WARNING: {qid} not found in benchmark")
            continue

        result = score_entry(entry, q_data, client)
        score_str = f"Score: {result['score']}" if result['score'] is not None else f"Parse failed: {result['raw_response'][:80]}"
        safe_print(f"  {qid} ({result['type']}): {score_str}")
        scores.append(result)

    output_path = args.output or str(batch_path.parent / batch_path.name.replace("batch_", "judge_"))
    output_file = Path(output_path)
    output_file.parent.mkdir(exist_ok=True)

    out_data = {
        "metadata": {
            "judge_model": JUDGE_MODEL,
            "provider": JUDGE_PROVIDER,
            "batch_file": batch_path.name,
            "total": len(scores),
            "timestamp": datetime.now().isoformat(),
        },
        "scores": scores,
    }

    output_file.write_text(json.dumps(out_data, ensure_ascii=False, indent=2), encoding="utf-8")
    safe_print(f"\nJudge results saved: {output_file}")

    scored = [s["score"] for s in scores if s["score"] is not None]
    if scored:
        safe_print(f"Mean score: {sum(scored) / len(scored):.2f} / 5.0  (n={len(scored)})")
    else:
        safe_print("WARNING: no scores parsed successfully")


if __name__ == "__main__":
    main()
