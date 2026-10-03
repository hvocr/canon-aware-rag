import json
from pathlib import Path

QUERIES = Path("data/queries.csv")
TRACES = ["Q005", "Q017", "Q019", "Q074", "Q086"]


def load(path):
    with Path(path).open(encoding="utf-8") as f:
        return {json.loads(l)["query_id"]: json.loads(l) for l in f}


vanilla = load("data/results_baseline.jsonl")
b2 = load("data/results_variant_a2.jsonl")
b3 = load("data/results_variant_c2.jsonl")

for qid in TRACES:
    print(f"\n{'=' * 70}")
    print(f"{qid}")
    print('=' * 70)
    v = vanilla.get(qid, {})
    print(f"\nQUERY: {v.get('query_text', '')}")
    print(f"TYPE:  {v.get('query_type', '')}")
    print(f"GT:    {v.get('ground_truth', '')}")

    for name, run in [("VANILLA", vanilla), ("B2", b2), ("B3", b3)]:
        r = run.get(qid, {})
        if not r:
            continue
        print(f"\n--- {name} ---")
        print(f"Retrieved branches: {r.get('retrieved_branches', [])}")
        if r.get("detected_branch"):
            print(f"Detected branch: {r['detected_branch']}")
        if r.get("mode"):
            print(f"Mode: {r['mode']}")
        print(f"Answer:\n{r.get('answer', '')[:600]}")