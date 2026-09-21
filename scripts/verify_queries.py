import csv
import json
from pathlib import Path

QUERIES = Path("data/queries.csv")
RAW = Path("data/raw")

corpus = {}
for f in RAW.glob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    corpus.setdefault(d["branch"], []).append(d["text"])


def find_support(term, branch):
    if branch not in corpus:
        return False
    for text in corpus[branch]:
        if term.lower() in text.lower():
            return True
    return False


def key_terms(ground_truth):
    words = [w.strip(".,;:()—\"") for w in ground_truth.split()]
    terms = [w for w in words if len(w) > 4][:4]
    return terms


with QUERIES.open(encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

results = {"likely_verified": [], "partial": [], "not_found": [], "skipped": []}

for row in rows:
    if row["status"] == "verified":
        continue

    branch = row["branch_expected"].strip()
    if not branch:
        results["skipped"].append(row["query_id"])
        continue

    terms = key_terms(row["ground_truth"])
    if not terms:
        results["skipped"].append(row["query_id"])
        continue

    hits = [t for t in terms if find_support(t, branch)]
    if len(hits) >= 2:
        results["likely_verified"].append(row["query_id"])
    elif len(hits) == 1:
        results["partial"].append((row["query_id"], hits[0]))
    else:
        results["not_found"].append(row["query_id"])

print(f"LIKELY VERIFIED ({len(results['likely_verified'])}):")
print(", ".join(results["likely_verified"]))
print()
print(f"PARTIAL ({len(results['partial'])}):")
for qid, term in results["partial"]:
    print(f"  {qid}: only '{term}' found")
print()
print(f"NOT FOUND ({len(results['not_found'])}):")
print(", ".join(results["not_found"]))
print()
print(f"SKIPPED (ambiguous/control) ({len(results['skipped'])}):")
print(", ".join(results["skipped"]))