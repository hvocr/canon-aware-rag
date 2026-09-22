import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS = Path("data/chunks.jsonl")
DB_DIR = Path("data/chroma_db")
COLLECTION = "canon_chunks"
MODEL_NAME = "BAAI/bge-small-en-v1.5"


def main():
    print(f"Loading embedding model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)

    print("Loading chunks...")
    chunks = []
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    print(f"  {len(chunks)} chunks")

    print("Encoding chunks...")
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    print("Building ChromaDB collection...")
    client = chromadb.PersistentClient(path=str(DB_DIR))

    # Delete existing collection if present
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )

    # Add in batches
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        collection.add(
            ids=[c["chunk_id"] for c in batch],
            documents=[c["text"] for c in batch],
            embeddings=embeddings[i : i + batch_size].tolist(),
            metadatas=[
                {
                    "branch": c["branch"],
                    "source_type": c["source_type"],
                    "parent_file": c["parent_file"],
                }
                for c in batch
            ],
        )
        print(f"  added {min(i + batch_size, len(chunks))}/{len(chunks)}")

    print(f"\nDone. Collection has {collection.count()} chunks.")
    print(f"Stored at: {DB_DIR}")


if __name__ == "__main__":
    main()