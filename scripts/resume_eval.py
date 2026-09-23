# scripts/resume_eval.py
import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from baseline_rag import answer

QUERIES = Path("data/queries.csv")
RESULTS = Path("data/results_baseline.jsonl")

# Load already-completed query IDs
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
        text = row["query_text"]
        print(f"[{i}/{len(rows)}] {qid}: {text[:60]}")
        try:
            result = answer(text)
            record = {
                "query_id": qid,
                "query_text": text,
                "query_type": row["query_type"],
                "conflict_type": row["conflict_type"],
                "branch_expected": row["branch_expected"],
                "ground_truth": row["ground_truth"],
                "answer": result["answer"],
                "retrieved_branches": [c["branch"] for c in result["reranked"]],
                "retrieved_chunk_ids": [c["chunk_id"] for c in result["reranked"]],
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.3)