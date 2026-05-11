import argparse
import json
import re
from pathlib import Path

import chromadb
import chromadb.errors
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

EXTRACTED_DIR = Path("data/extracted")
PROCESSED_DIR = Path("data/processed")
CHROMADB_DIR = Path("data/chromadb")
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150

COLLECTIONS = {
    "a": {"name": "rag_papers_raw", "desc": "testo grezzo da PDF"},
    "b": {"name": "rag_papers", "desc": "Markdown compilato"},
}

model = SentenceTransformer("all-MiniLM-L6-v2")


def smart_chunk_text(text: str, doc_name: str) -> list[dict]:
    text = re.sub(r"--- PAGE \d+ ---", "", text)
    text = re.sub(r"^\*Total.*?\*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    paragraphs = text.split("\n\n")
    chunks = []
    buffer = ""
    char_acc = 0

    for para in paragraphs:
        para = para.strip()
        if not para or len(para) < 15:
            continue

        if len(buffer) + len(para) < CHUNK_SIZE:
            buffer += ("\n\n" if buffer else "") + para
            char_acc += len(para) + 2
            continue

        if buffer:
            chunks.append({
                "text": buffer.strip(),
                "doc_name": doc_name,
                "char_count": len(buffer.strip()),
            })
            overlap = buffer[-CHUNK_OVERLAP:] if len(buffer) > CHUNK_OVERLAP else buffer
            buffer = overlap + "\n\n" + para
        else:
            chunks.append({
                "text": para,
                "doc_name": doc_name,
                "char_count": len(para),
            })
            buffer = ""

    if buffer:
        chunks.append({
            "text": buffer.strip(),
            "doc_name": doc_name,
            "char_count": len(buffer.strip()),
        })

    return [c for c in chunks if c["char_count"] > 40]


def load_pipeline_a() -> list[dict]:
    """Carica testo grezzo dalle estrazioni JSON."""
    json_files = sorted(EXTRACTED_DIR.glob("*.json"))
    all_chunks = []
    for jpath in tqdm(json_files, desc="Chunking raw text"):
        with open(jpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        doc_name = jpath.stem
        text_parts = []
        for page in data["pages"]:
            text_parts.append(f"--- PAGE {page['page_num']} ---")
            text_parts.append(page["text"])
        raw_text = "\n".join(text_parts)
        chunks = smart_chunk_text(raw_text, doc_name)
        all_chunks.extend(chunks)
        tqdm.write(f"  {doc_name}: {len(chunks)} chunks")
    return all_chunks


def load_pipeline_b() -> list[dict]:
    """Carica testo dai file Markdown compilati."""
    md_files = sorted(PROCESSED_DIR.glob("*.md"))
    all_chunks = []
    for md_path in tqdm(md_files, desc="Chunking Markdown"):
        text = md_path.read_text(encoding="utf-8")
        chunks = smart_chunk_text(text, md_path.stem)
        all_chunks.extend(chunks)
        tqdm.write(f"  {md_path.name}: {len(chunks)} chunks")
    return all_chunks


def main():
    parser = argparse.ArgumentParser(description="Build ChromaDB index")
    parser.add_argument(
        "--pipeline", choices=["a", "b"], default="b",
        help="Pipeline A: raw PDF text, Pipeline B: Markdown compilato (default: b)"
    )
    args = parser.parse_args()

    pipeline = args.pipeline
    col_info = COLLECTIONS[pipeline]
    print(f"Pipeline {pipeline.upper()} — {col_info['desc']}")

    if pipeline == "a":
        all_chunks = load_pipeline_a()
    else:
        all_chunks = load_pipeline_b()

    print(f"\nTotali chunks: {len(all_chunks)}")
    print("Generazione embedding con all-MiniLM-L6-v2...")

    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    print("Scrittura su ChromaDB...")
    client = chromadb.PersistentClient(
        path=str(CHROMADB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )

    collection_name = col_info["name"]
    try:
        client.delete_collection(collection_name)
    except (ValueError, chromadb.errors.NotFoundError):
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 100
    for i in tqdm(range(0, len(all_chunks), batch_size), desc="ChromaDB insert"):
        batch = all_chunks[i:i + batch_size]
        batch_emb = embeddings[i:i + batch_size]
        ids = [f"chunk_{i + j}" for j in range(len(batch))]
        metadatas = [
            {"doc_name": c["doc_name"], "char_count": c["char_count"]}
            for c in batch
        ]
        documents = [c["text"] for c in batch]
        collection.add(
            ids=ids,
            embeddings=batch_emb.tolist(),
            metadatas=metadatas,
            documents=documents,
        )

    print(f"\nIndice creato: '{collection_name}' con {len(all_chunks)} chunks")
    metadata_path = CHROMADB_DIR / f"chunks_metadata_{pipeline}.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "pipeline": pipeline,
            "total_chunks": len(all_chunks),
            "collection": collection_name,
            "chunks": [{
                "id": f"chunk_{i}",
                "doc_name": c["doc_name"],
                "char_count": c["char_count"],
                "preview": c["text"][:150],
            } for i, c in enumerate(all_chunks)]
        }, f, ensure_ascii=False, indent=2)
    print(f"Metadata salvati in {metadata_path}")


if __name__ == "__main__":
    main()
