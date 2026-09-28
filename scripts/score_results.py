import csv
import json
import re
from pathlib import Path

QUERIES = Path("data/queries.csv")
BASELINE = Path("data/results_baseline.jsonl")
VARIANT_A = Path("data/results_variant_a.jsonl")
VARIANT_A2 = Path("data/results_variant_a2.jsonl")

with QUERIES.open(encoding="utf-8") as f:
    queries = {r["query_id"]: r for r in csv.DictReader(f)}


def load(path):
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return {json.loads(l)["query_id"]: json.loads(l) for l in f}


def retrieval_precision(record):
    expected = record.get("branch_expected", "").strip()
    if not expected:
        return None
    branches = record["retrieved_branches"]
    if not branches:
        return 0.0
    return sum(1 for b in branches if b == expected) / len(branches)


# Tightened: require TWO DIFFERENT version identifiers, not just 2 keywords
VERSION_TOKENS = {
    "novel": ["novel", "book"],
    "kubrick": ["kubrick"],
    "1979": ["1979"],
    "1980": ["1980", "kubrick"],
    "1997": ["1997"],
    "1990": ["1990", "uncut"],
    "1994": ["1994"],
    "2020": ["2020"],
    "2004": ["2004"],
    "2024": ["2024"],
    "film": ["film", "movie"],
    "miniseries": ["miniseries"],
}


def conflict_surfaced(record):
    """For AMBIGUOUS: does the answer mention at least TWO distinct versions?"""
    ans = record["answer"].lower()
    if not ans or ans == "[empty_response]":
        return False

    versions_mentioned = set()
    for version_name, tokens in VERSION_TOKENS.items():
        for tok in tokens:
            if tok in ans:
                versions_mentioned.add(version_name)
                break

    return len(versions_mentioned) >= 2


def is_empty(record):
    return not record["answer"] or record["answer"] == "[EMPTY_RESPONSE]"


def score(results, name):
    by_type = {}
    for qid, rec in results.items():
        if qid not in queries:
            continue
        t = queries[qid]["query_type"]
        b = by_type.setdefault(t, {
            "total": 0, "empty": 0,
            "prec_sum": 0.0, "prec_n": 0,
            "surfaced": 0, "ambig": 0,
        })
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
        if b["prec_n"]:
            prec = f"{b['prec_sum'] / b['prec_n']:.2f}"
        else:
            prec = "—"
        surf = f"{b['surfaced']}/{b['ambig']}" if b["ambig"] else "—"
        print(f"{t:<12} {b['total']:>4} {b['empty']:>6} {prec:>10} {surf:>18}")


score(load(BASELINE), "BASELINE")
score(load(VARIANT_A), "VARIANT A (keyword)")
score(load(VARIANT_A2), "VARIANT A2 (LLM)")