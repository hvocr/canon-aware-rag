import json
import re
from pathlib import Path

CHUNKS = Path("data/chunks.jsonl")

# Phrases that signal a conflict is being described
PATTERNS = [
    r"unlike (the|his|her|its) (novel|book|film|miniseries|adaptation)",
    r"in (the|this) (novel|book|film|miniseries|adaptation)",
    r"(differs|different) from",
    r"whereas",
    r"however.*(novel|book|film|miniseries|adaptation)",
    r"(changed|altered|modified) (the|his|her|its)",
    r"instead of",
    r"rather than",
    r"in contrast",
    r"the (novel|book|film|miniseries|adaptation) (version|adaptation|depiction)",
    r"(novel|book|film|miniseries|adaptation) (Barlow|Flagg|Hallorann|Jack|Susan|Callahan|Kid)",
]


def main():
    hits = []
    with CHUNKS.open(encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            text_lower = rec["text"].lower()
            for pat in PATTERNS:
                m = re.search(pat, text_lower)
                if m:
                    hits.append(rec)
                    break

    print(f"Found {len(hits)} candidate chunks\n")
    for rec in hits:
        print(f"--- {rec['chunk_id']} | {rec['branch']} ---")
        print(rec["text"][:400])
        print()


if __name__ == "__main__":
    main()