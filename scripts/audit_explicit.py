import csv
import json
from pathlib import Path

QUERIES = Path("data/queries.csv")
RESULT_FILES = [
    "data/results_baseline.jsonl",
    "data/results_variant_a.jsonl",
    "data/results_variant_a2.jsonl",
    "data/results_variant_c2.jsonl",
    "data/results_ablation_retrieval_only.jsonl",
    "data/results_ablation_prompt_only.jsonl",
]
OUT = Path("data/explicit_audit.txt")

with QUERIES.open(encoding="utf-8") as f:
    queries = {r["query_id"]: r for r in csv.DictReader(f)}


def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return {json.loads(l)["query_id"]: json.loads(l) for l in f}


runs = {Path(p).stem: load(p) for p in RESULT_FILES if Path(p).exists()}


def clean(s):
    """Replace narrow no-break spaces and other exotic whitespace with regular spaces."""
    if not s:
        return ""
    for bad in ["\u202f", "\u2009", "\u00a0"]:
        s = s.replace(bad, " ")
    return s


with OUT.open("w", encoding="utf-8") as out:
    for qid in sorted(queries):
        q = queries[qid]
        if q["query_type"] != "EXPLICIT":
            continue
        out.write(f"\n{'=' * 78}\n")
        out.write(f"{qid} | Branch: {q['branch_expected']}\n")
        out.write(f"QUERY: {clean(q['query_text'])}\n")
        out.write(f"GROUND TRUTH: {clean(q['ground_truth'])}\n\n")
        for name, run in runs.items():
            if qid in run:
                ans = clean(run[qid].get("answer", "").strip().replace("\n", " "))[:300]
                out.write(f"  [{name[:20]:<20}] {ans}\n")