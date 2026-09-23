import os
from pathlib import Path

from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer, CrossEncoder
from groq import Groq

load_dotenv()

DB_DIR = Path("data/chroma_db")
COLLECTION = "canon_chunks"
EMBED_MODEL = "BAAI/bge-small-en-v1.5"
RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
GROQ_MODEL = "openai/gpt-oss-120b"

_embed = None
_rerank = None
_collection = None


def _init():
    global _embed, _rerank, _collection
    if _embed is None:
        print("Loading models (first call only)...")
        _embed = SentenceTransformer(EMBED_MODEL)
        _rerank = CrossEncoder(RERANK_MODEL)
        client = chromadb.PersistentClient(path=str(DB_DIR))
        _collection = client.get_collection(COLLECTION)
        print("Models ready.")


def retrieve(query, k_retrieve=20):
    _init()
    q_emb = _embed.encode([query], normalize_embeddings=True).tolist()
    results = _collection.query(query_embeddings=q_emb, n_results=k_retrieve)
    return [
        {
            "chunk_id": cid,
            "text": text,
            "branch": meta["branch"],
            "distance": float(dist),
        }
        for cid, meta, text, dist in zip(
            results["ids"][0],
            results["metadatas"][0],
            results["documents"][0],
            results["distances"][0],
        )
    ]


def rerank(query, candidates, k_rerank=5):
    _init()
    pairs = [(query, c["text"]) for c in candidates]
    scores = _rerank.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [{**c, "rerank_score": float(s)} for c, s in ranked[:k_rerank]]


def generate(query, contexts):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    context_block = "\n\n".join(
        f"[{i+1}] ({c['branch']}) {c['text']}" for i, c in enumerate(contexts)
    )
    prompt = (
        "Answer the question using only the provided context. "
        "If the answer depends on which version of the story is being asked about, "
        "say so. Do not make up facts.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {query}\n\n"
        "Answer:"
    )
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()


def answer(query, k_retrieve=20, k_rerank=5):
    candidates = retrieve(query, k_retrieve)
    top = rerank(query, candidates, k_rerank)
    ans = generate(query, top)
    return {
        "query": query,
        "retrieved": candidates,
        "reranked": top,
        "answer": ans,
    }


if __name__ == "__main__":
    r = answer("Does Dick Hallorann survive in the novel?")
    print("\nANSWER:", r["answer"])
    print("\nTOP-5 BRANCHES:")
    for c in r["reranked"]:
        print(f"  [{c['rerank_score']:.2f}] {c['branch']}")