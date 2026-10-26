import csv
from collections import defaultdict
from pathlib import Path

CSV = Path("data/judge_validation.csv")

rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
total = len(rows)
agree = sum(1 for r in rows if r["human_verdict"].strip().lower() == "agree")
disagree = sum(1 for r in rows if r["human_verdict"].strip().lower() == "disagree")
missing = total - agree - disagree

print(f"Total rows: {total}")
print(f"Agree: {agree}")
print(f"Disagree: {disagree}")
print(f"Missing label: {missing}")
if total > 0:
    print(f"Agreement rate: {agree/total:.1%}")
print()

by_type = defaultdict(lambda: {"n": 0, "agree": 0})
for r in rows:
    t = r["query_type"]
    by_type[t]["n"] += 1
    if r["human_verdict"].strip().lower() == "agree":
        by_type[t]["agree"] += 1

print(f"{'Type':<12} {'N':>4} {'Agree':>6} {'Rate':>8}")
for t in ["EXPLICIT", "IMPLICIT", "AMBIGUOUS", "CONTROL"]:
    if t in by_type:
        b = by_type[t]
        rate = b["agree"] / b["n"] if b["n"] else 0
        print(f"{t:<12} {b['n']:>4} {b['agree']:>6} {rate:>7.1%}")