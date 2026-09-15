# Literature Notes

## Paper: ConflictRAG: Detecting and Resolving Knowledge Conflicts in Retrieval-Augmented Generation

- Link: https://arxiv.org/pdf/2605.17301
- Problem: Retrieval-Augmented Generation (RAG) systems implicitly
  assume mutual consistency among retrieved documents. It is an
  assumption that frequently fails in practice because retrieved
  documents may contain mutually contradictory information
- Method: Detect-classify-resolve pipeline. Two-stage detection
  (embedding MLP+LLM refinement), Entropy-TOPSIS credibility scoring,
  CARS evaluation metric. 
- Gap it leaves: ConflictRAG assumes conflicts can be resolved by
  ranking source credibility(newer>older, authoritative>less).
  This fails when sources are parallel valid branches with no universal
  hierarchy—as in fictional canon, where the "correct" source is
  user-specified, not system-determined.
  They resolve conflict; we preserve it.


## Paper: TruthfulRAG
- Link: https://arxiv.org/abs/2511.10375
- Problem: RAG systems face factual-level conflicts between retrieved
  external knowledge and the LLM's internal parametric knowledge.
  Existing token-level and semantic-level methods are too coarse-grained
  to capture fine-grained factual discrepancies.
- Method: Builds Knowledge Graphs from retrieved content via triple
  extraction. Uses query-based graph retrieval and entropy-based
  filtering to locate and resolve conflicting triples before generation.
- Gap it leaves: Assumes conflicts have a single correct resolution
  (the KG-consistent fact). Fails when sources are parallel valid
  branches with no universal hierarchy — as in fiction canon, where
  the user's specified branch determines correctness, not graph
  consistency or source credibility.
---

