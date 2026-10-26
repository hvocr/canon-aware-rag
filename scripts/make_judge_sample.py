import csv
import json
import random
from pathlib import Path

random.seed(42)

QUERIES = Path("data/queries.csv")
SCORE_FILES = {
    "vanilla": "data/answer_scores_vanilla.jsonl",
    "b1": "data/answer_scores_b1.jsonl",
    "b2": "data/answer_scores_b2.jsonl",
    "b3": "data/answer_scores_b3.jsonl",
    "retrieval_only": "data/answer_scores_retrieval_only.jsonl",
    "prompt_only": "data/answer_scores_prompt_only.jsonl",
}
RESULT_FILES = {
    "vanilla": "data/results_baseline.jsonl",
    "b1": "data/results_variant_a.jsonl",
    "b2": "data/results_variant_a2.jsonl",
    "b3": "data/results_variant_c2.jsonl",
    "retrieval_only": "data/results_ablation_retrieval_only.jsonl",
    "prompt_only": "data/results_ablation_prompt_only.jsonl",
}
OUT = Path("data/judge_validation.csv")


def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return {json.loads(l)["query_id"]: json.loads(l) for l in f}


with QUERIES.open(encoding="utf-8") as f:
    queries = {r["query_id"]: r for r in csv.DictReader(f)}

scores = {name: load(p) for name, p in SCORE_FILES.items()}
results = {name: load(p) for name, p in RESULT_FILES.items()}

# Sample 10 per query type, random config for each
by_type = {"EXPLICIT": [], "IMPLICIT": [], "AMBIGUOUS": [], "CONTROL": []}
for qid, q in queries.items():
    t = q["query_type"]
    if t in by_type:
        by_type[t].append(qid)

rows = []
for qtype, qids in by_type.items():
    sampled = random.sample(qids, min(10, len(qids)))
    for qid in sampled:
        config = random.choice(list(SCORE_FILES.keys()))
        if qid not in scores[config] or qid not in results[config]:
            continue
        q = queries[qid]
        rows.append({
            "config": config,
            "query_id": qid,
            "query_type": q["query_type"],
            "query_text": q["query_text"],
            "ground_truth": q["ground_truth"],
            "answer": results[config][qid]["answer"].replace("\n", " ")[:500],
            "judge_score": scores[config][qid]["score"],
            "human_verdict": "",
        })

with OUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "config", "query_id", "query_type", "query_text", "ground_truth",
        "answer", "judge_score", "human_verdict",
    ])
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to {OUT}")