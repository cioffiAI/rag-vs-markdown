import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import chromadb
import chromadb.errors
from chromadb.config import Settings
from openai import OpenAI
from sentence_transformers import SentenceTransformer

CHROMADB_DIR = Path("data/chromadb")
LOGS_DIR = Path("data/logs")
LOGS_DIR.mkdir(exist_ok=True)
TOP_K = 3
LLM_MODEL = "qwen3.5-0.8b"
LM_STUDIO_URL = "http://localhost:1234/v1"
OLLAMA_URL = "http://localhost:11434/v1"
EMBED_MODEL = "all-MiniLM-L6-v2"

embedder = SentenceTransformer(EMBED_MODEL)

client = chromadb.PersistentClient(
    path=str(CHROMADB_DIR),
    settings=Settings(anonymized_telemetry=False),
)
collection = client.get_collection("rag_papers")

import httpx
llm_client = None
llm_source = None
for name, url in [("LM Studio", LM_STUDIO_URL), ("Ollama", OLLAMA_URL)]:
    try:
        r = httpx.get(url.replace("/v1", "") + "/api/tags" if "ollama" in url else url, timeout=2)
        if r.status_code < 400:
            llm_client = OpenAI(base_url=url, api_key="not-needed")
            llm_source = name
            print(f"LLM backend: {name} ({url})")
            break
    except Exception:
        continue
if llm_client is None:
    print("WARNING: Nessun LLM server rilevato (LM Studio :1234 o Ollama :11434)")
    print("Avvia LM Studio con Qwen 2.5 0.8B o Ollama per usare query.py")

SYSTEM_PROMPT = """You are a precise RAG assistant. Answer the user's question using ONLY the provided context chunks.

Rules:
- If the context contains enough information, answer concisely.
- If the context does NOT contain enough information, say "I cannot find sufficient information in the provided documents to answer this question."
- Cite the source document name(s) in your answer.
- Do NOT use prior knowledge or make up information.
- Be specific and factual."""

def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    query_emb = embedder.encode([query], convert_to_numpy=True)
    results = collection.query(
        query_embeddings=query_emb.tolist(),
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "text": doc,
            "doc_name": meta["doc_name"],
            "score": round(1.0 - dist, 4),
        })
    return chunks

def build_prompt(question: str, chunks: list[dict]) -> str:
    context_parts = []
    for i, c in enumerate(chunks):
        context_parts.append(
            f"[Document {i+1}: {c['doc_name']}]\n{c['text']}"
        )
    context = "\n\n".join(context_parts)
    prompt = f"{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    return prompt

def ask_llm(prompt: str) -> str:
    if llm_client is None:
        return "[ERROR: Nessun LLM server disponibile. Avvia LM Studio o Ollama.]"
    try:
        resp = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=256,
            timeout=90,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[ERROR LLM: {e}]"

def answer(question: str, log: bool = True) -> dict:
    chunks = retrieve(question)
    prompt = build_prompt(question, chunks)
    answer_text = ask_llm(prompt)
    result = {
        "question": question,
        "answer": answer_text,
        "retrieved_chunks": chunks,
        "timestamp": datetime.now().isoformat(),
    }
    if log:
        log_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_path = LOGS_DIR / f"query_{log_id}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        result["log_file"] = str(log_path)
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python query.py <question>")
        print("   or: python query.py --file <path_to_questions.json>")
        sys.exit(1)

    if sys.argv[1] == "--file":
        qpath = Path(sys.argv[2])
        with open(qpath, "r", encoding="utf-8") as f:
            questions = json.load(f)
        results = []
        for q in questions if isinstance(questions, list) else questions["questions"]:
            question_text = q.get("question", q.get("query", ""))
            if not question_text:
                continue
            print(f"\n---\nQ: {question_text}")
            result = answer(question_text)
            print(f"A: {result['answer'][:200]}...")
            results.append(result)
        out_path = LOGS_DIR / f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nBatch completato. Risultati salvati in {out_path}")
    else:
        question = " ".join(sys.argv[1:])
        result = answer(question)
        print(f"\nDomanda: {result['question']}")
        print(f"Risposta: {result['answer']}")
        print(f"\nChunk sorgente: {result['retrieved_chunks'][0]['doc_name']}")
        print(f"Log: {result.get('log_file', 'N/A')}")

if __name__ == "__main__":
    main()
