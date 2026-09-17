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


## Paper: Authority Bias in RAG (ACL 2025)
- Link: https://aclanthology.org/2025.acl-long.1400/
- Problem: When user-provided knowledge conflicts with retrieved database
  knowledge, LLMs tend to favor the user even when the user is factually
  wrong. This "Authority Bias" makes RAG systems vulnerable to
  user-provided misinformation. Existing RAG systems synthesize knowledge
  from user prompts and external databases without handling this conflict.
- Method: The first systematic characterization of Authority Bias across
  six LLMs and diverse tasks. Introduces the Authority Bias Detection
  Dataset (ABDD) and new metrics. Proposes Conflict Detection Enhanced
  Query (CDEQ): identifies conflicting sentences, assesses credibility,
  augments query to detect perturbed text, reducing bias.
- Gap it leaves: Assumes user input is a factual claim that can be wrong,
  and that retrieved facts represent ground truth. Fails when the user's
  input is a provenance specification (e.g., "in the novel" or "in the
  1997 miniseries") rather than a claim. In canon-aware retrieval, the
  user selects a valid branch; there is no single ground truth to
  correct toward. Authority Bias resolves conflict by favoring facts;
  canon-aware retrieval preserves conflict by respecting user-selected
  provenance.


## Paper: MAGIC (EMNLP 2025 Findings)
- Link: https://aclanthology.org/2025.findings-emnlp.466/
- Problem: Existing benchmarks for knowledge conflict in RAG have three
  limitations: narrow focus on QA setup, heavy reliance on entity
  substitution techniques, and restricted range of conflict types.
  This limits our understanding of how LLMs handle conflicts.
- Method: KG-based framework that generates varied and subtle conflicts
  between two similar yet distinct contexts, with interpretability through
  the explicit relational structure of KGs. Creates MAGIC benchmark.
  Experiments show both open-source and proprietary models struggle with
  conflict detection, especially multi-hop reasoning, and often fail to
  pinpoint exact sources of contradictions.
- Gap it leaves: Conflicts are synthetically generated from knowledge
  graphs via entity manipulation. Real-world conflicts in fiction arise
  from independent creative decisions, not entity substitution. Moreover,
  MAGIC still assumes one source is correct and asks which the model
  trusts. It does not address the case where multiple sources are all
  valid branches and the user selects which one to use.


## Paper: Resolving Conflicting Evidence in Automated Fact-Checking (IJCAI 2025)
- Link: https://www.ijcai.org/proceedings/2025/1073
- Problem: RAG systems for fact-checking become unreliable when confronted
  with conflicting evidence from sources of varying credibility. No prior
  systematic evaluation of RAG under such conflicts existed.
- Method: Introduces CONFACT, a dataset of questions paired with conflicting
  information from various sources. Evaluates state-of-the-art RAG methods,
  identifies vulnerabilities in resolving conflicts from media source
  credibility differences. Investigates integrating media background
  information into retrieval and generation stages. Shows source credibility
  integration significantly improves conflict resolution.
- Gap it leaves: Assumes conflicts have a credibility hierarchy — some
  sources are more reliable than others, and the system should rank them.
  This fails when sources are parallel valid branches with no credibility
  hierarchy, as in fictional canon, where the novel, film, and miniseries
  are all equally valid and the "correct" one is user-specified. Credibility-
  ranking resolves conflict by choosing the most reliable source; canon-aware
  retrieval preserves conflict by respecting the user's branch selection.


## Paper: ConRAG
- Link: https://scipublication.com/index.php/JACS/article/view/257/234
- Problem: Retrieved passages can be "all relevant yet mutually inconsistent."
  Baseline RAG merges them silently. ConRAG makes conflict explicit.
- Method: Tags passages as Support / Refute / Irrelevant. Clusters into
  consistent evidence groups. Computes a conflict score. When conflict is
  high, preserves both sides in the evidence packet. Generation follows a
  "sort-adjudicate-cite" protocol: outputs stance (Support / Refute / NEI),
  an evidence table, and sentence-level citations. Abstains (NEI) when
  evidence is balanced.
- Evaluation: FEVER, SciFact (stance + evidence), ALCE (citation precision/
  recall), RAGTruth (hallucination). All fact-checking benchmarks where a
  ground truth exists.
- Gap it leaves: ConRAG treats conflict as epistemic uncertainty — it
  asks "which source is correct?" and abstains (NEI) when it can't tell.
  This assumes a single ground truth exists even when the system can't
  determine it. We study a domain — fiction canon — where no branch is
  universally correct. The user's branch specification determines the
  answer. Our ambiguous case is not "we don't know" but "the answer
  depends on which version you mean." ConRAG resolves by adjudication;
  we resolve by respecting user-specified provenance.
---
