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

BRANCHES = [
    "SHINING_NOVEL", "SHINING_KUBRICK", "SHINING_1997",
    "STAND_NOVEL_1978", "STAND_NOVEL_1990", "STAND_1994", "STAND_2020",
    "SALEMS_LOT_NOVEL", "SALEMS_LOT_1979", "SALEMS_LOT_2004", "SALEMS_LOT_2024",
]

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


# --- Classifier: identical to variant_a2.py (long prompt) ---
def classify_branch(query):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = (
        "Classify which canon branch this question refers to. "
        "Branches:\n"
        "- SHINING_NOVEL = Stephen King's 1977 novel The Shining\n"
        "- SHINING_KUBRICK = Kubrick's 1980 film The Shining\n"
        "- SHINING_1997 = 1997 TV miniseries The Shining\n"
        "- STAND_NOVEL_1978 = The Stand original 1978 edition\n"
        "- STAND_NOVEL_1990 = The Stand 1990 uncut edition\n"
        "- STAND_1994 = 1994 The Stand miniseries\n"
        "- STAND_2020 = 2020 The Stand miniseries\n"
        "- SALEMS_LOT_NOVEL = 1975 novel Salem's Lot\n"
        "- SALEMS_LOT_1979 = 1979 Salem's Lot miniseries\n"
        "- SALEMS_LOT_2004 = 2004 Salem's Lot miniseries\n"
        "- SALEMS_LOT_2024 = 2024 Salem's Lot film\n"
        "- NONE = query does not specify a branch\n\n"
        "If the question names or clearly implies one branch, output that label only. "
        "Otherwise output NONE. Output only the label, nothing else.\n\n"
        f"Question: {query}\nLabel:"
    )
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=1500,
    )
    label = resp.choices[0].message.content.strip().upper()
    if label in BRANCHES:
        return label
    return None


def retrieve(query, k=20, branch=None):
    _init()
    q_emb = _embed.encode([query], normalize_embeddings=True).tolist()
    where = {"branch": branch} if branch else None
    results = _collection.query(query_embeddings=q_emb, n_results=k, where=where)
    return [
        {"chunk_id": cid, "text": t, "branch": m["branch"], "distance": float(d)}
        for cid, m, t, d in zip(
            results["ids"][0], results["metadatas"][0],
            results["documents"][0], results["distances"][0],
        )
    ]


def retrieve_per_branch(query, k_per_branch=3):
    """Retrieve top-k from every branch separately, then merge."""
    all_chunks = []
    for branch in BRANCHES:
        all_chunks.extend(retrieve(query, k=k_per_branch, branch=branch))
    return all_chunks


def rerank(query, candidates, k=5):
    _init()
    if not candidates:
        return []
    scores = _rerank.predict([(query, c["text"]) for c in candidates])
    ranked = sorted(zip(candidates, scores), key=lambda x: -x[1])
    return [{**c, "rerank_score": float(s)} for c, s in ranked[:k]]


def generate_specific(query, contexts):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    block = "\n\n".join(f"[{i+1}] ({c['branch']}) {c['text']}" for i, c in enumerate(contexts))
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


def generate_ambiguous(query, contexts):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    block = "\n\n".join(f"[{i+1}] ({c['branch']}) {c['text']}" for i, c in enumerate(contexts))
    prompt = (
        "The user did not specify a version. Answer the question for EACH version "
        "represented in the context. Structure your answer as bullet points:\n"
        "- In <version>: <answer>\n"
        "If only one version appears in the context, say so explicitly. "
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
    branch = classify_branch(query)
    if branch:
        candidates = retrieve(query, k=20, branch=branch)
        top = rerank(query, candidates, k=5)
        ans = generate_specific(query, top)
        mode = "specific"
    else:
        candidates = retrieve_per_branch(query, k_per_branch=3)
        top = rerank(query, candidates, k=10)
        ans = generate_ambiguous(query, top)
        mode = "ambiguous"

    return {
        "query": query,
        "detected_branch": branch,
        "mode": mode,
        "retrieved": candidates,
        "reranked": top,
        "answer": ans,
    }


if __name__ == "__main__":
    for q in [
        "Does Dick Hallorann survive in the novel The Shining?",
        "Does Dick Hallorann survive The Shining?",
        "How does Jack Torrance die?",
    ]:
        print(f"\n=== {q}")
        r = answer(q)
        print(f"Detected: {r['detected_branch']} | Mode: {r['mode']}")
        print(f"Answer:\n{r['answer'][:500]}")
        print(f"Branches retrieved: {sorted(set(c['branch'] for c in r['reranked']))}")