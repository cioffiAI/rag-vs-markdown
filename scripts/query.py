import argparse
import json
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

COLLECTIONS = {
    "a": "rag_papers_raw",
    "b": "rag_papers",
}

embedder = SentenceTransformer(EMBED_MODEL)

client = chromadb.PersistentClient(
    path=str(CHROMADB_DIR),
    settings=Settings(anonymized_telemetry=False),
)

import httpx
llm_client = None
llm_source = None
for name, url in [("LM Studio", LM_STUDIO_URL), ("Ollama", OLLAMA_URL)]:
    try:
        r = httpx.get(url.replace("/v1", "") + "/api/tags" if "ollama" in url else url, timeout=2)
        if r.status_code < 400:
            llm_client = OpenAI(base_url=url, api_key="not-needed")
            llm_source = name
            break
    except Exception:
        continue
if llm_client is None:
    print("WARNING: Nessun LLM server rilevato (LM Studio :1234 o Ollama :11434)")

SYSTEM_PROMPT = """You are a precise RAG assistant. Answer the user's question using ONLY the provided context chunks.

Rules:
- If the context contains enough information, answer concisely.
- If the context does NOT contain enough information, say "I cannot find sufficient information in the provided documents to answer this question."
- Cite the source document name(s) in your answer.
- Do NOT use prior knowledge or make up information.
- Be specific and factual."""


def get_collection(pipeline: str):
    col_name = COLLECTIONS.get(pipeline, "rag_papers")
    try:
        return client.get_collection(col_name)
    except (ValueError, chromadb.errors.NotFoundError):
        print(f"ERROR: Collezione '{col_name}' non trovata. Esegui build_index.py --pipeline {pipeline} prima.")
        sys.exit(1)


def retrieve(query: str, collection, k: int = TOP_K) -> list[dict]:
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


def answer(question: str, collection, log: bool = True) -> dict:
    chunks = retrieve(question, collection)
    prompt = build_prompt(question, chunks)
    answer_text = ask_llm(prompt)
    result = {
        "question": question,
        "answer": answer_text,
        "retrieved_chunks": chunks,
        "timestamp": datetime.now().isoformat(),
        "pipeline": collection.name,
    }
    if log:
        log_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_path = LOGS_DIR / f"query_{log_id}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        result["log_file"] = str(log_path)
    return result


def main():
    parser = argparse.ArgumentParser(description="Query ChromaDB RAG index")
    parser.add_argument("question", nargs="*", help="Domanda da porre")
    parser.add_argument("--pipeline", choices=["a", "b"], default="b",
                        help="Pipeline da usare (default: b)")
    parser.add_argument("--file", type=str, help="File JSON con domande multiple")
    parser.add_argument("--tag", type=str, default="", help="Suffisso per il file di log batch")
    args = parser.parse_args()

    collection = get_collection(args.pipeline)
    print(f"Pipeline {args.pipeline.upper()} — collezione '{collection.name}'")

    if args.file:
        qpath = Path(args.file)
        with open(qpath, "r", encoding="utf-8") as f:
            questions = json.load(f)
        q_list = questions if isinstance(questions, list) else questions["questions"]
        results = []
        def safe_print(msg: str):
            try:
                print(msg)
            except UnicodeEncodeError:
                print(msg.encode("ascii", "replace").decode("ascii"))

        tag = f"_{args.tag}" if args.tag else f"_{args.pipeline}"
        out_path = LOGS_DIR / f"batch{tag}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        for i, q in enumerate(q_list):
            question_text = q.get("question", q.get("query", ""))
            if not question_text:
                continue
            safe_print(f"\n---\nQ: {question_text[:80]}...")
            result = answer(question_text, collection)
            safe_print(f"A: {result['answer'][:200]}...")
            results.append(result)
            if (i + 1) % 10 == 0:
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                safe_print(f"[Checkpoint] {i+1}/{len(q_list)} salvati in {out_path}")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        safe_print(f"\nBatch completato. Risultati salvati in {out_path}")
    else:
        if not args.question:
            parser.print_help()
            sys.exit(1)
        question = " ".join(args.question)
        result = answer(question, collection)
        print(f"\nDomanda: {result['question']}")
        print(f"Risposta: {result['answer']}")
        print(f"\nChunk sorgente: {result['retrieved_chunks'][0]['doc_name']}")
        print(f"Pipeline: {result['pipeline']}")
        print(f"Log: {result.get('log_file', 'N/A')}")


if __name__ == "__main__":
    main()
