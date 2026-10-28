import csv
import json
from collections import defaultdict
from pathlib import Path

QUERIES = Path("data/queries.csv")
CHUNKS = Path("data/chunks.jsonl")

with QUERIES.open(encoding="utf-8") as f:
    queries = {r["query_id"]: r for r in csv.DictReader(f)}

# Count chunks per branch
chunk_counts = defaultdict(int)
with CHUNKS.open(encoding="utf-8") as f:
    for line in f:
        chunk_counts[json.loads(line)["branch"]] += 1


def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return {json.loads(l)["query_id"]: json.loads(l) for l in f}


def per_branch(results, name):
    by_branch = defaultdict(lambda: {"n": 0, "prec_sum": 0.0})
    for qid, rec in results.items():
        expected = rec.get("branch_expected", "").strip()
        if not expected:
            continue
        branches = rec["retrieved_branches"]
        if not branches:
            continue
        p = sum(1 for b in branches if b == expected) / len(branches)
        by_branch[expected]["n"] += 1
        by_branch[expected]["prec_sum"] += p

    print(f"\n=== {name} ===")
    print(f"{'Branch':<22} {'Chunks':>6} {'Queries':>7} {'RetrPrec':>10}")
    for b in sorted(by_branch, key=lambda x: -chunk_counts.get(x, 0)):
        stats = by_branch[b]
        prec = stats["prec_sum"] / stats["n"] if stats["n"] else 0
        print(f"{b:<22} {chunk_counts.get(b, 0):>6} {stats['n']:>7} {prec:>10.2f}")


per_branch(load("data/results_baseline.jsonl"), "VANILLA")
per_branch(load("data/results_variant_a2.jsonl"), "B2 (Classifier)")
per_branch(load("data/results_variant_c2.jsonl"), "B3 (Classifier + PB)")