# Literature Notes

## Paper: ConflictRAG: Detecting and Resolving Knowledge Conflicts in Retrieval-Augmented Generation

- **Link:**
- https://arxiv.org/pdf/2605.17301
- **Problem:**
- Retrieval-Augmented Generation (RAG) systems implicitly assume mutual consistency among retrieved documents. It is an assumption that frequently fails in practice because
  retrieved documents may contain mutually contradictory information
- **Method:**
  Detect-classify-resolve pipeline. Two-stage detection (embedding MLP + LLM refinement), Entropy-TOPSIS credibility scoring, CARS evaluation metric. 
- **Gap it leaves:**
  ConflictRAG assumes conflicts can be resolved by ranking source credibility (newer > older, authoritative > less).
  This fails when sources are parallel valid branches with no universal hierarchy — as in fictional canon, where the "correct" source is user-specified, not system-determined.
  They resolve conflict; we preserve it.
---
