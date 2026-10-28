import json
from statsmodels.stats.contingency_tables import mcnemar

def load_scores(path):
    try:
        return {json.loads(l)["query_id"]: json.loads(l)["score"] for l in open(path, encoding="utf-8")}
    except FileNotFoundError:
        print(f"Error: Could not find {path}")
        return {}

def load_types(path):
    try:
        return {json.loads(l)["query_id"]: json.loads(l)["query_type"] for l in open(path, encoding="utf-8")}
    except FileNotFoundError:
        print(f"Error: Could not find {path}")
        return {}

# 1. Load the scores and query types
vanilla = load_scores("data/answer_scores_vanilla.jsonl")
b2 = load_scores("data/answer_scores_b2.jsonl")
univ = load_scores("data/answer_scores_control.jsonl")
q_types = load_types("data/results_baseline.jsonl")

if not vanilla or not b2 or not univ:
    exit()

# 2. Build McNemar table for EXPLICIT: Vanilla vs B2
# (Testing if the massive retrieval gain from B2 actually improved answers)
table_explicit = [[0, 0], [0, 0]] 
# row 0: Vanilla wrong, row 1: Vanilla right
# col 0: B2 wrong, col 1: B2 right

for qid, q_type in q_types.items():
    if q_type == "EXPLICIT":
        v = vanilla.get(qid, 0)
        b = b2.get(qid, 0)
        table_explicit[v][b] += 1

print("=== EXPLICIT: Vanilla vs B2 ===")
print(f"Table: {table_explicit}")
print(f"McNemar p-value: {mcnemar(table_explicit, exact=True).pvalue:.4f}\n")

# 3. Build McNemar table for AMBIGUOUS: Vanilla vs Universal
# (Testing if the generation prompt significantly improved conflict surfacing)
table_ambig = [[0, 0], [0, 0]]
for qid, q_type in q_types.items():
    if q_type == "AMBIGUOUS":
        v = vanilla.get(qid, 0)
        u = univ.get(qid, 0)
        table_ambig[v][u] += 1

print("=== AMBIGUOUS: Vanilla vs Universal-Prompt ===")
print(f"Table: {table_ambig}")
print(f"McNemar p-value: {mcnemar(table_ambig, exact=True).pvalue:.4f}")