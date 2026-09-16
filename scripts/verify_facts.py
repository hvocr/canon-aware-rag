import csv
import json
from pathlib import Path

SEED = Path("data/seed_facts.csv")
RAW = Path("data/raw")

# Load all corpus text into memory, keyed by branch
corpus = {}
for f in RAW.glob("*.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    corpus.setdefault(d["branch"], []).append(d["text"])


def search(term, branch):
    """Return up to 2 snippets containing term in the given branch."""
    if branch not in corpus:
        return ["[no chunks for this branch]"]
    hits = []
    term_lower = term.lower()
    for text in corpus[branch]:
        idx = text.lower().find(term_lower)
        if idx != -1:
            start = max(0, idx - 80)
            end = min(len(text), idx + 200)
            hits.append("..." + text[start:end].replace("\n", " ") + "...")
            if len(hits) >= 2:
                break
    return hits or ["[NOT FOUND]"]


# Key term to search per fact — pick the most distinctive word
KEY_TERMS = {
    "SH-001": "Hallorann", "SH-002": "Hallorann", "SH-003": "Hallorann",
    "SH-004": "217", "SH-005": "237",
    "SH-006": "boiler", "SH-007": "maze", "SH-008": "explode",
    "SH-012": "alcohol", "SH-013": "madness",
    "SH-015": "blonde", "SH-016": "brunette",
    "SH-017": "Kid", "SH-018": "Kid",
    "SH-021": "Trashcan", "SH-022": "Trashcan",
    "SH-023": "opening", "SH-024": "opening",
    "SH-025": "1990", "SH-026": "1990", "SH-027": "2020",
    "SH-028": "Abagail", "SH-029": "Abagail", "SH-030": "Abagail",
    "SL-001": "Barlow", "SL-002": "Nosferatu", "SL-003": "Hauer", "SL-004": "2024",
    "SL-005": "Straker", "SL-006": "Straker",
    "SL-007": "Susan", "SL-008": "Susan",
    "SL-009": "Callahan", "SL-010": "Callahan", "SL-011": "Callahan",
    "SL-012": "epilogue", "SL-013": "epilogue",
}


with SEED.open(encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        fid = row["fact_id"]
        term = KEY_TERMS.get(fid)
        if not term:
            continue
        print(f"\n=== {fid} | {row['work']} | {row['event']} | {row['branch']} ===")
        print(f"Claim: {row['fact_value']}")
        for snippet in search(term, row["branch"]):
            print(f"  > {snippet}")