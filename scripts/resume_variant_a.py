import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from variant_a import answer

QUERIES = Path("data/queries.csv")
RESULTS = Path("data/results_variant_a.jsonl")

done = set()
if RESULTS.exists():
    with RESULTS.open(encoding="utf-8") as f:
        for line in f:
            done.add(json.loads(line)["query_id"])
print(f"Already done: {len(done)}")

with QUERIES.open(encoding="utf-8") as f:
    rows = [r for r in csv.DictReader(f) if r["query_id"] not in done]

print(f"Remaining: {len(rows)}\n")

with RESULTS.open("a", encoding="utf-8") as out:
    for i, row in enumerate(rows, 1):
        qid = row["query_id"]
        print(f"[{i}/{len(rows)}] {qid}")
        try:
            result = answer(row["query_text"])
            out.write(json.dumps({
                "query_id": qid,
                "query_text": row["query_text"],
                "query_type": row["query_type"],
                "conflict_type": row["conflict_type"],
                "branch_expected": row["branch_expected"],
                "ground_truth": row["ground_truth"],
                "detected_branch": result["detected_branch"],
                "answer": result["answer"],
                "retrieved_branches": [c["branch"] for c in result["reranked"]],
                "retrieved_chunk_ids": [c["chunk_id"] for c in result["reranked"]],
            }, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.3)