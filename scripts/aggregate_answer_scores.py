import json
from collections import defaultdict
from pathlib import Path

VARIANTS = {
    "vanilla": "data/answer_scores_vanilla.jsonl",
    "b2": "data/answer_scores_b2.jsonl",
    "b3": "data/answer_scores_b3.jsonl",
    "retrieval_only": "data/answer_scores_retrieval_only.jsonl",
    "prompt_only": "data/answer_scores_prompt_only.jsonl",
}


def summarize(path):
    if not Path(path).exists():
        return None
    by_type = defaultdict(lambda: {"n": 0, "correct": 0})
    with open(path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            t = rec["query_type"]
            by_type[t]["n"] += 1
            by_type[t]["correct"] += rec["score"]
    return by_type


print(f"{'Variant':<16} {'Type':<12} {'N':>4} {'Correct':>8} {'Rate':>6}")
print("-" * 52)
for name, path in VARIANTS.items():
    by_type = summarize(path)
    if not by_type:
        continue
    for t in ["EXPLICIT", "IMPLICIT", "AMBIGUOUS", "CONTROL"]:
        if t not in by_type:
            continue
        b = by_type[t]
        rate = b["correct"] / b["n"] if b["n"] else 0
        print(f"{name:<16} {t:<12} {b['n']:>4} {b['correct']:>8} {rate:>6.2f}")
    print()