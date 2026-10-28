# Results

| Variant | EXPLICIT RetrPrec | IMPLICIT RetrPrec | AMBIGUOUS ConflictSurfaced |
|---|---|---|---|
| Baseline | 0.46 | 0.41 | 16/24 |
| A (keyword branch detection) | 0.54 | 0.39 | 19/24 |
| A2 (LLM branch classification) | 0.98 | 0.54 | 13/24 |
| C2 (A2 + per-branch retrieval fallback) | 0.97 | 0.41 | 20/24 |

## Findings

1. Branch-aware retrieval nearly eliminates cross-branch retrieval 
   for EXPLICIT queries (0.46 → 0.98).
2. LLM-based branch classification (A2) over-commits on AMBIGUOUS 
   queries, reducing conflict surfacing below baseline (16 → 13).
3. Per-branch retrieval (C2) recovers AMBIGUOUS conflict surfacing 
   (13 → 20) but reduces IMPLICIT retrieval precision (0.54 → 0.41).
4. No single variant dominates. Branch-aware retrieval requires 
   recognizing both when a branch is specified and when it is not.