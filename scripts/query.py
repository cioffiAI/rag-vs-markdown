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
OPENROUTER_URL = "https://openrouter.ai/api/v1"
OPENCODE_ZEN_URL = "https://opencode.ai/zen/v1"
OPENCODE_GO_URL = "https://opencode.ai/zen/go/v1"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta"

COLLECTIONS = {
    "a": "rag_papers_raw",
    "b": "rag_papers",
    "c": "rag_papers_md_filtered",
}

embedder = None

client = chromadb.PersistentClient(
    path=str(CHROMADB_DIR),
    settings=Settings(anonymized_telemetry=False),
)

import httpx
import os
import time

llm_client = None
llm_source = None

def _detect_provider(provider_arg: str):
    if provider_arg == "gemini":
        key = os.environ.get("GEMINI_API_KEY", "")
        if not key:
            print("WARNING: GEMINI_API_KEY non impostata. Imposta con $env:GEMINI_API_KEY = '...'")
            return None, None, None
        return "Gemini", GEMINI_URL, key
    if provider_arg:
        name_map = {
            "lm-studio": ("LM Studio", LM_STUDIO_URL),
            "ollama": ("Ollama", OLLAMA_URL),
            "openrouter": ("OpenRouter", OPENROUTER_URL),
            "opencode-zen": ("OpenCode-Zen", OPENCODE_ZEN_URL),
            "opencode-go": ("OpenCode-Go", OPENCODE_GO_URL),
        }
        name, url = name_map[provider_arg]
        key = os.environ.get("OPENROUTER_API_KEY", "") if provider_arg in ("openrouter", "opencode-zen", "opencode-go") else "not-needed"
        if provider_arg in ("openrouter", "opencode-zen", "opencode-go") and not key:
            print("WARNING: OPENROUTER_API_KEY non impostata.")
            return None, None, None
        return name, url, key
    for name, url in [("LM Studio", LM_STUDIO_URL), ("Ollama", OLLAMA_URL)]:
        try:
            r = httpx.get(url.replace("/v1", "") + "/api/tags" if "ollama" in url else url, timeout=2)
            if r.status_code < 400:
                return name, url, "not-needed"
        except Exception:
            continue
    return None, None, None

SYSTEM_PROMPT = """You are a precise RAG assistant. Answer the user's question using ONLY the provided context chunks.

Rules:
- If the context contains enough information, answer concisely.
- If the context does NOT contain enough information, say "I cannot find sufficient information in the provided documents to answer this question."
- Cite the source document name(s) in your answer.
- Do NOT use prior knowledge or make up information.
- Be specific and factual."""


def get_collection(pipeline: str, embedder_name: str = "all-MiniLM-L6-v2"):
    suffix = "" if embedder_name == "all-MiniLM-L6-v2" else f"_{embedder_name.replace('/', '_')}"
    col_name = COLLECTIONS.get(pipeline, "rag_papers") + suffix
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


_last_request_time = 0.0

def _ask_gemini(prompt: str, model: str, api_key: str) -> str:
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
                timeout=120,
            )
            _last_request_time = time.time()
            if r.status_code == 429 and attempt < 2:
                wait = 10 * (attempt + 1)
                print(f"  [Rate limit Gemini, attendo {wait}s...]")
                time.sleep(wait)
                continue
            if r.status_code != 200:
                return f"[ERROR LLM: Gemini HTTP {r.status_code} - {r.text[:200]}]"
            data = r.json()
            candidates = data.get("candidates", [])
            if not candidates:
                return "[ERROR LLM: Gemini returned no candidates]"
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not text:
                return "[ERROR LLM: Gemini returned empty text]"
            return text.strip()
        except Exception as e:
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            return f"[ERROR LLM: {e}]"
    return "[ERROR LLM: Max retries]"

def ask_llm(prompt: str, model: str = "", api_key: str = "", max_tokens: int = 256) -> str:
    global _last_request_time
    model_name = model or LLM_MODEL
    if llm_source == "Gemini":
        return _ask_gemini(prompt, model_name, api_key)
    if llm_client is None:
        return "[ERROR: Nessun LLM server disponibile.]"
    if llm_source in ("OpenRouter", "OpenCode-Zen", "OpenCode-Go"):
        wait_time = 3.0 if llm_source == "OpenRouter" else 1.0
        elapsed = time.time() - _last_request_time
        if elapsed < wait_time:
            time.sleep(wait_time - elapsed)
    for attempt in range(3):
        try:
            resp = llm_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=max_tokens,
                timeout=120,
                extra_headers={"HTTP-Referer": "https://github.com/cioffiAI/rag-vs-markdown",
                               "X-Title": "RAG-vs-Markdown"} if llm_source == "OpenRouter" else {},
            )
            _last_request_time = time.time()
            msg = resp.choices[0].message
            content = msg.content
            if not content:
                rc = getattr(msg, 'reasoning_content', None)
                if rc:
                    return rc.strip()
                reason = getattr(resp.choices[0], 'finish_reason', 'unknown')
                return f"[ERROR LLM: Empty response (finish_reason={reason})]"
            return content.strip()
        except Exception as e:
            err_str = str(e)
            if "429" in err_str and attempt < 2:
                wait = 5 * (attempt + 1)
                print(f"  [Rate limit, attendo {wait}s...]")
                time.sleep(wait)
                continue
            return f"[ERROR LLM: {e}]"
    return "[ERROR LLM: Max retries]"


_gemini_key = ""

def answer(question: str, collection, log: bool = True, model: str = "", max_tokens: int = 256) -> dict:
    chunks = retrieve(question, collection)
    prompt = build_prompt(question, chunks)
    answer_text = ask_llm(prompt, model, api_key=_gemini_key, max_tokens=max_tokens)
    result = {
        "question": question,
        "answer": answer_text,
        "retrieved_chunks": chunks,
        "timestamp": datetime.now().isoformat(),
        "pipeline": collection.name,
        "model": model or LLM_MODEL,
    }
    if log:
        log_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_path = LOGS_DIR / f"query_{log_id}.json"
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        result["log_file"] = str(log_path)
    return result


def main():
    parser = argparse.ArgumentParser(description="Query ChromDB RAG index")
    parser.add_argument("question", nargs="*", help="Domanda da porre")
    parser.add_argument("--pipeline", choices=["a", "b", "c"], default="b",
                        help="Pipeline da usare (default: b)")
    parser.add_argument("--file", type=str, help="File JSON con domande multiple")
    parser.add_argument("--tag", type=str, default="", help="Suffisso per il file di log batch")
    parser.add_argument("--model", type=str, default="",
                        help="Nome del modello LLM (default: qwen3.5-0.8b)")
    parser.add_argument("--provider", choices=["lm-studio", "ollama", "openrouter", "opencode-zen", "opencode-go", "gemini"], default="",
                        help="Provider LLM (default: auto-detect)")
    parser.add_argument("--max-tokens", type=int, default=256,
                        help="Max tokens per risposta (default: 256)")
    parser.add_argument("--embedder", type=str, default="all-MiniLM-L6-v2",
                        help="Modello sentence-transformers per embedding (default: all-MiniLM-L6-v2)")
    args = parser.parse_args()

    global llm_client, llm_source, _gemini_key, embedder
    embedder = SentenceTransformer(args.embedder)
    name, url, key = _detect_provider(args.provider)
    if name:
        if name == "Gemini":
            _gemini_key = key
            llm_source = name
        else:
            llm_client = OpenAI(base_url=url, api_key=key)
            llm_source = name
        print(f"Provider: {llm_source}")
    else:
        print("WARNING: Nessun LLM server rilevato.")

    collection = get_collection(args.pipeline, args.embedder)
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
            result = answer(question_text, collection, model=args.model, max_tokens=args.max_tokens)
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
        result = answer(question, collection, model=args.model, max_tokens=args.max_tokens)
        print(f"\nDomanda: {result['question']}")
        print(f"Risposta: {result['answer']}")
        print(f"\nChunk sorgente: {result['retrieved_chunks'][0]['doc_name']}")
        print(f"Pipeline: {result['pipeline']}")
        print(f"Modello: {result['model']}")
        print(f"Log: {result.get('log_file', 'N/A')}")


if __name__ == "__main__":
    main()
