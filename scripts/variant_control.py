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
        _embed = SentenceTransformer(EMBED_MODEL)
        _rerank = CrossEncoder(RERANK_MODEL)
        client = chromadb.PersistentClient(path=str(DB_DIR))
        _collection = client.get_collection(COLLECTION)


def retrieve(query, k=20):
    _init()
    q_emb = _embed.encode([query], normalize_embeddings=True).tolist()
    results = _collection.query(query_embeddings=q_emb, n_results=k)
    return [
        {"chunk_id": cid, "text": t, "branch": m["branch"], "distance": float(d)}
        for cid, m, t, d in zip(
            results["ids"][0], results["metadatas"][0],
            results["documents"][0], results["distances"][0],
        )
    ]


def rerank(query, candidates, k=5):
    _init()
    if not candidates:
        return []
    scores = _rerank.predict([(query, c["text"]) for c in candidates])
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [{**c, "rerank_score": float(s)} for c, s in ranked[:k]]


def generate_control_prompt(query, contexts):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    block = "\n\n".join(f"[{i+1}] ({c['branch']}) {c['text']}" for i, c in enumerate(contexts))
    
    # THIS IS THE CONTROL PROMPT. 
    # We removed "The user did not specify a version" so it doesn't break EXPLICIT queries.
    # We apply this to EVERY query.
    prompt = (
        "Answer the question using the provided context. "
        "If multiple versions of the story are represented in the context, "
        "answer for EACH version separately. Structure your answer as bullet points:\n"
        "- In <version>: <answer>\n"
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
    # Always global retrieval
    candidates = retrieve(query, k=20)
    top = rerank(query, candidates, k=5)
    
    # Always per-branch prompt
    ans = generate_control_prompt(query, top)
    
    return {
        "query": query,
        "detected_branch": None,
        "mode": "control",
        "retrieved": candidates,
        "reranked": top,
        "answer": ans,
    }