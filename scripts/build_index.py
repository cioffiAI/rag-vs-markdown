import json
import os
import re
from pathlib import Path
import chromadb
import chromadb.errors
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

PROCESSED_DIR = Path("data/processed")
CHROMADB_DIR = Path("data/chromadb")
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 150

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


def main():
    md_files = sorted(PROCESSED_DIR.glob("*.md"))
    print(f"Indicizzazione {len(md_files)} documenti Markdown...")

    all_chunks = []
    for md_path in tqdm(md_files, desc="Chunking"):
        text = md_path.read_text(encoding="utf-8")
        chunks = smart_chunk_text(text, md_path.stem)
        all_chunks.extend(chunks)
        tqdm.write(f"  {md_path.name}: {len(chunks)} chunks")

    print(f"\nTotali chunks: {len(all_chunks)}")
    print("Generazione embedding con all-MiniLM-L6-v2...")

    texts = [c["text"] for c in all_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    print("Scrittura su ChromaDB...")
    client = chromadb.PersistentClient(
        path=str(CHROMADB_DIR),
        settings=Settings(anonymized_telemetry=False),
    )

    collection_name = "rag_papers"
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
    metadata_path = CHROMADB_DIR / "chunks_metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "total_chunks": len(all_chunks),
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
