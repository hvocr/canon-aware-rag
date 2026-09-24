import json
from pathlib import Path

RESULTS = Path("data/results_baseline.jsonl")
KEEP = Path("data/results_baseline_clean.jsonl")

kept = []
removed = 0
with RESULTS.open(encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        if rec["answer"] and len(rec["answer"].strip()) >= 5 and rec["answer"] != "[EMPTY_RESPONSE]":
            kept.append(line)
        else:
            removed += 1

with KEEP.open("w", encoding="utf-8") as f:
    f.writelines(kept)

print(f"Kept {len(kept)}, removed {removed}")
print("Renaming clean file to results_baseline.jsonl...")

KEEP.replace(RESULTS)
print("Done. Now run resume_eval.py.")