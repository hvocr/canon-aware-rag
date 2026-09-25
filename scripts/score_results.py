import csv
import json
from pathlib import Path

QUERIES = Path("data/queries.csv")
BASELINE = Path("data/results_baseline.jsonl")
VARIANT_A = Path("data/results_variant_a.jsonl")

with QUERIES.open(encoding="utf-8") as f:
    queries = {r["query_id"]: r for r in csv.DictReader(f)}


def load(path):
    with path.open(encoding="utf-8") as f:
        return {json.loads(l)["query_id"]: json.loads(l) for l in f}


def retrieval_precision(record):
    """Fraction of top-5 chunks from the expected branch. None if not applicable."""
    expected = record.get("branch_expected", "").strip()
    if not expected:
        return None
    branches = record["retrieved_branches"]
    return sum(1 for b in branches if b == expected) / len(branches)


def conflict_surfaced(record):
    """For AMBIGUOUS: does the answer mention more than one branch/version?"""
    ans = record["answer"].lower()
    if not ans or ans == "[empty_response]":
        return False
    markers = ["version", "adaptation", "novel", "film", "miniseries", "depends",
               "differ", "varies", "in the book", "in the 19", "in the 20"]
    return sum(1 for m in markers if m in ans) >= 2


def is_empty(record):
    return not record["answer"] or record["answer"] == "[EMPTY_RESPONSE]"


def score(results, name):
    by_type = {}
    for qid, rec in results.items():
        q = queries[qid]
        t = q["query_type"]
        by_type.setdefault(t, {"total": 0, "empty": 0, "prec_sum": 0, "prec_n": 0, "surfaced": 0, "ambig": 0})
        b = by_type[t]
        b["total"] += 1
        if is_empty(rec):
            b["empty"] += 1
        p = retrieval_precision(rec)
        if p is not None:
            b["prec_sum"] += p
            b["prec_n"] += 1
        if t == "AMBIGUOUS":
            b["ambig"] += 1
            if conflict_surfaced(rec):
                b["surfaced"] += 1

    print(f"\n=== {name} ===")
    print(f"{'Type':<12} {'N':>4} {'Empty':>6} {'RetrPrec':>10} {'ConflictSurfaced':>18}")
    for t in ["EXPLICIT", "IMPLICIT", "AMBIGUOUS", "CONTROL"]:
        if t not in by_type:
            continue
        b = by_type[t]
        prec = b["prec_sum"] / b["prec_n"] if b["prec_n"] else 0
        surf = f"{b['surfaced']}/{b['ambig']}" if b["ambig"] else "—"
        print(f"{t:<12} {b['total']:>4} {b['empty']:>6} {prec:>10.2f} {surf:>18}")


baseline = load(BASELINE)
variant_a = load(VARIANT_A)

score(baseline, "BASELINE")
score(variant_a, "VARIANT A")