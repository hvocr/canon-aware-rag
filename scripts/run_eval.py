import csv
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from baseline_rag import answer

QUERIES = Path("data/queries.csv")
OUT = Path("data/results_baseline.jsonl")

with QUERIES.open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print(f"Running {len(rows)} queries\n")

with OUT.open("w", encoding="utf-8") as out:
    for i, row in enumerate(rows, 1):
        qid = row["query_id"]
        text = row["query_text"]
        print(f"[{i}/{len(rows)}] {qid} ({row['query_type']}): {text[:70]}")
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

print(f"\nDone. Saved to {OUT}")