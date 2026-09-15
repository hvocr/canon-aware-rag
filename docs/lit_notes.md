# Literature Notes

## Paper: ConflictRAG
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


## Paper: Narrative Knowledge Weaver (NKW) 
- Link: https://arxiv.org/abs/2606.05724
- Problem: Long-form narrative QA requires reasoning over evolving story
  worlds — changing character states, causal triggers, temporal position,
  and later consequences. Existing RAG units (chunks, entities, relations)
  don't encode how evidence functions inside a story. Two mismatches:
  (1) narrative evidence is functional not just locational, (2) characters
  and relations are dynamic.
- Method: Source-grounded framework aligning textual evidence, atomic facts,
  canonical graph structure, entity profiles, interactions, episodes, and
  storylines. Query-time text/graph/narrative tools with post-retrieval
  reading skills to assemble evidence and audit actor, scope, polarity,
  state, and temporal constraints.
- Gap it leaves: Assumes a single coherent story world. The "canonical
  graph structure" presumes consistency. Fails when the story world
  fractures into parallel branches (adaptations, editions, retcons) where
  the same character or event has incompatible facts across versions.
  NKW handles dynamic states within one canon; we handle conflict across
  multiple canons.


## Paper: T-GRAG
- Link: https://dl.acm.org/doi/10.1145/3746027.3755628
- Problem: Existing GraphRAG methods ignore temporal dynamics of knowledge,
  leading to temporal ambiguity, time-insensitive retrieval, and semantic
  redundancy. They treat facts as static.
- Method: Temporal GraphRAG with five components: Temporal Knowledge Graph
  Generator (time-stamped evolving graphs), Temporal Query Decomposition,
  Three-layer Interactive Retriever (progressive filtering across temporal
  subgraphs), Source Text Extractor, and LLM Generator. Introduces
  Time-LongQA benchmark from corporate annual reports.
- Gap it leaves: Assumes a single evolving timeline where newer facts
  supersede older ones. This fails for canon branches — parallel,
  non-hierarchical versions of the same story (novel vs. film vs. edition)
  where the "correct" version depends on user specification, not recency.
  Temporal conflicts have a resolution rule (newest wins); canon conflicts
  have no resolution rule — the user picks the branch.
---

