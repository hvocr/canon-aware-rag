import os
import re
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

# Map from query keywords to branch labels
BRANCH_KEYWORDS = {
    "SHINING_NOVEL": ["novel", "book", "1977"],
    "SHINING_KUBRICK": ["kubrick", "1980 film", "nicholson"],
    "SHINING_1997": ["1997", "miniseries", "garris"],
    "STAND_NOVEL_1978": ["1978", "original novel"],
    "STAND_NOVEL_1990": ["1990", "uncut", "complete"],
    "STAND_1994": ["1994 miniseries"],
    "STAND_2020": ["2020", "paramount", "cbs"],
    "SALEMS_LOT_NOVEL": ["1975 novel", "the novel salem"],
    "SALEMS_LOT_1979": ["1979", "tobe hooper"],
    "SALEMS_LOT_2004": ["2004", "rutger hauer", "rob lowe"],
    "SALEMS_LOT_2024": ["2024", "dauberman"],
}


def detect_branch(query):
    """Return branch label if the query names one, else None."""
    q = query.lower()
    for branch, keywords in BRANCH_KEYWORDS.items():
        for kw in keywords:
            if kw in q:
                return branch
    return None


_embed = None
_rerank = None
_collection = None


def _init():
    global _embed, _rerank, _collection
    if _embed is None:
        print("Loading models...")
        _embed = SentenceTransformer(EMBED_MODEL)
        _rerank = CrossEncoder(RERANK_MODEL)
        client = chromadb.PersistentClient(path=str(DB_DIR))
        _collection = client.get_collection(COLLECTION)


def retrieve(query, k=20, branch=None):
    _init()
    q_emb = _embed.encode([query], normalize_embeddings=True).tolist()
    where = {"branch": branch} if branch else None
    results = _collection.query(query_embeddings=q_emb, n_results=k, where=where)
    return [
        {"chunk_id": cid, "text": text, "branch": meta["branch"], "distance": float(dist)}
        for cid, meta, text, dist in zip(
            results["ids"][0],
            results["metadatas"][0],
            results["documents"][0],
            results["distances"][0],
        )
    ]


def rerank(query, candidates, k=5):
    _init()
    pairs = [(query, c["text"]) for c in candidates]
    scores = _rerank.predict(pairs)
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [{**c, "rerank_score": float(s)} for c, s in ranked[:k]]


def generate(query, contexts):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    block = "\n\n".join(
        f"[{i+1}] ({c['branch']}) {c['text']}" for i, c in enumerate(contexts)
    )
    prompt = (
        "Answer the question using only the provided context. "
        "If the answer depends on which version of the story is being asked about, say so. "
        "Do not make up facts.\n\n"
        f"Context:\n{block}\n\nQuestion: {query}\n\nAnswer:"
    )
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=1500,
    )
    ans = resp.choices[0].message.content.strip()
    return ans if ans and len(ans) >= 5 else "[EMPTY_RESPONSE]"


def answer(query):
    branch = detect_branch(query)
    if branch:
        candidates = retrieve(query, k=20, branch=branch)
    else:
        candidates = retrieve(query, k=20)
    top = rerank(query, candidates, k=5)
    return {
        "query": query,
        "detected_branch": branch,
        "retrieved": candidates,
        "reranked": top,
        "answer": generate(query, top),
    }


if __name__ == "__main__":
    for q in ["Does Dick Hallorann survive in the novel The Shining?",
              "Does Dick Hallorann survive The Shining?"]:
        print(f"\n=== {q}")
        r = answer(q)
        print(f"Detected branch: {r['detected_branch']}")
        print(f"Answer: {r['answer'][:300]}")
        print("Branches retrieved:", [c["branch"] for c in r["reranked"]])