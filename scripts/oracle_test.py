import argparse
import json
import sys
import os
import time
from datetime import datetime
from pathlib import Path

import httpx

EXTRACTED_DIR = Path("data/extracted")
LOGS_DIR = Path("data/logs")
BENCHMARK_PATH = Path("data/benchmark_questions.json")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"

MAX_ORACLE_CHARS = 50000

PROMPT_TEMPLATE = """You are a precise RAG assistant. Answer the user's question using ONLY the provided context chunks.

Rules:
- If the context contains enough information, answer concisely.
- If the context does NOT contain enough information, say "I cannot find sufficient information in the provided documents to answer this question."
- Cite the source document name(s) in your answer.
- Do NOT use prior knowledge or make up information.
- Be specific and factual.

ORACLE CONTEXT:
{context}

Question: {question}

Answer:"""


def load_benchmark():
    with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_oracle_text(doc_name: str) -> str:
    stem = doc_name.replace(".pdf", "")
    path = EXTRACTED_DIR / f"{stem}.json"
    if not path.exists():
        print(f"  WARNING: File non trovato: {path}")
        return ""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    pages = data.get("pages", [])
    text_parts = []
    total_chars = 0
    for page in pages:
        page_text = page.get("text", "")
        header = f"--- PAGE {page['page_num']} ---"
        text_parts.append(header)
        text_parts.append(page_text)
        total_chars += len(header) + 1 + len(page_text)
        if total_chars > MAX_ORACLE_CHARS:
            break
    text = "\n".join(text_parts)
    print(f"  Oracle text: {stem} ({len(pages)} pages, {len(text)} chars)")
    return text


def build_oracle_prompt(question: str, doc_texts: dict[str, str]) -> str:
    context_parts = []
    for i, (doc_name, text) in enumerate(doc_texts.items()):
        if text:
            context_parts.append(f"[Document {i+1}: {doc_name}]\n{text}")
    context = "\n\n".join(context_parts)
    return PROMPT_TEMPLATE.format(context=context, question=question)


_last_request_time = 0.0


def ask_gemini(prompt: str, model: str, api_key: str) -> str:
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < 4.0:
        time.sleep(4.0 - elapsed)
    for attempt in range(3):
        try:
            r = httpx.post(
                f"{GEMINI_URL}/models/{model}:generateContent",
                headers={"X-goog-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 256},
                },
                timeout=60,
            )
            _last_request_time = time.time()
            if r.status_code == 429 and attempt < 2:
                wait = 10 * (attempt + 1)
                print(f"  [Rate limit, attendo {wait}s...]")
                time.sleep(wait)
                continue
            if r.status_code != 200:
                return f"[ERROR LLM: HTTP {r.status_code} - {r.text[:200]}]"
            data = r.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return "[ERROR LLM: no candidates]"
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not text:
                return "[ERROR LLM: empty text]"
            return text.strip()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return f"[ERROR LLM: {e}]"
    return "[ERROR LLM: Max retries]"


def main():
    parser = argparse.ArgumentParser(description="Oracle context test — raw extracted text as oracle context")
    parser.add_argument("--model", type=str, default="gemma-4-26b-a4b-it",
                        help="Modello LLM (default: gemma-4-26b-a4b-it)")
    parser.add_argument("--tag", type=str, default="oracle",
                        help="Suffisso per file output")
    parser.add_argument("--start", type=int, default=0,
                        help="Indice partenza (0-based)")
    parser.add_argument("--end", type=int, default=999,
                        help="Indice fine (esclusivo)")
    args = parser.parse_args()

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY non impostata.")
        sys.exit(1)

    benchmark = load_benchmark()
    questions = benchmark["questions"]

    print(f"Modello: {args.model}")
    print(f"Domande: {len(questions)}")
    print(f"Max chars per documento: {MAX_ORACLE_CHARS}")

    tag = f"_{args.tag}" if args.tag else ""
    out_path = LOGS_DIR / f"oracle{tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    results = []

    start_idx = args.start
    end_idx = min(args.end, len(questions))
    questions = questions[start_idx:end_idx]
    print(f"Indici: {start_idx}-{end_idx-1} ({len(questions)} domande)")

    for i, q in enumerate(questions):
        qid = q["id"]
        question_text = q.get("question", "")
        expected_docs = q.get("documents", [])

        print(f"\n--- [{i+1}/{len(questions)}] {qid}: {question_text[:80]}...")

        doc_texts = {}
        for doc_name in expected_docs:
            text = load_oracle_text(doc_name)
            if text:
                doc_texts[doc_name] = text

        if not doc_texts:
            print(f"  WARNING: Nessun documento trovato per {expected_docs}")
            results.append({
                "question": question_text,
                "answer": "[ERROR ORACLE: no documents found]",
                "oracle_docs": expected_docs,
                "oracle_char_count": 0,
                "timestamp": datetime.now().isoformat(),
                "model": args.model,
            })
            continue

        prompt = build_oracle_prompt(question_text, doc_texts)
        total_chars = sum(len(t) for t in doc_texts.values())
        answer_text = ask_gemini(prompt, args.model, api_key)

        print(f"  A: {answer_text[:150]}...")

        results.append({
            "question": question_text,
            "answer": answer_text,
            "oracle_docs": list(doc_texts.keys()),
            "oracle_char_count": total_chars,
            "timestamp": datetime.now().isoformat(),
            "model": args.model,
        })

        if (i + 1) % 10 == 0:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"  [Checkpoint] {i+1}/{len(questions)} salvati")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    errors = sum(1 for r in results if r["answer"].startswith("[ERROR"))
    print(f"\n{'='*50}")
    print(f"Oracle test completato: {out_path}")
    print(f"Errori: {errors}/{len(results)}")


if __name__ == "__main__":
    main()
