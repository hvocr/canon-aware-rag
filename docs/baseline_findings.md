# Baseline Findings

## Failure modes observed

1. **Retrieval imbalance** — Kubrick (98 chunks) and STAND_NOVEL_1978 (81) 
   dominate retrieval. Explicit novel queries retrieve 3–4 Kubrick chunks 
   because more Kubrick content exists.
   
2. **Cross-branch contamination** — Chunks labeled one branch describe 
   another. Q012 confused 2004 miniseries with the novel.

3. **Silent branch resolution** — AMBIGUOUS queries (Q019, Q031, Q062, Q094, 
   Q104) pick one branch and answer as fact, never acknowledging the conflict.

4. **Hallucination** — Q074 invented James Cromwell as Callahan's 2004 actor.

5. **Empty responses** — 15 queries returned empty answers from Groq. 
   Re-run with fallback handling.

## By query type

| Type | Approx. failure rate |
|---|---|
| EXPLICIT | 30% |
| IMPLICIT | 28% |
| AMBIGUOUS | 48% |
| CONTROL | 10% |