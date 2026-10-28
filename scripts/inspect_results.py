import json
from pathlib import Path

RESULTS = Path("data/results_baseline.jsonl")

with RESULTS.open(encoding="utf-8") as f:
    rows = [json.loads(l) for l in f]

print(f"Total results: {len(rows)}\n")

for r in rows:
    print(f"{r['query_id']} [{r['query_type']}] {r['query_text'][:60]}")
    print(f"  BRANCHES: {r['retrieved_branches']}")
    print(f"  ANS: {r['answer'][:250]}")
    print()