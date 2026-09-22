from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = Path("data/chroma_db")
COLLECTION = "canon_chunks"
MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(MODEL_NAME)
client = chromadb.PersistentClient(path=str(DB_DIR))
collection = client.get_collection(COLLECTION)


def search(query, k=5, branch=None):
    q_emb = model.encode([query], normalize_embeddings=True).tolist()
    where = {"branch": branch} if branch else None
    results = collection.query(
        query_embeddings=q_emb,
        n_results=k,
        where=where,
    )
    return list(zip(
        results["ids"][0],
        results["metadatas"][0],
        results["documents"][0],
        results["distances"][0],
    ))


if __name__ == "__main__":
    query = "Does Dick Hallorann survive in the novel?"
    print(f"Query: {query}\n")

    print("--- No filter ---")
    for cid, meta, text, dist in search(query):
        print(f"[{dist:.3f}] {meta['branch']:<20} {text[:120]}...")

    print("\n--- Filter: SHINING_NOVEL ---")
    for cid, meta, text, dist in search(query, branch="SHINING_NOVEL"):
        print(f"[{dist:.3f}] {meta['branch']:<20} {text[:120]}...")

    print("\n--- Filter: SHINING_KUBRICK ---")
    for cid, meta, text, dist in search(query, branch="SHINING_KUBRICK"):
        print(f"[{dist:.3f}] {meta['branch']:<20} {text[:120]}...")