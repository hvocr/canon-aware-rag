# Related Work

## Conflict-Aware Retrieval-Augmented Generation

Retrieval-Augmented Generation (RAG) grounds large language model outputs
in external knowledge, but its core pipeline implicitly assumes that
retrieved documents are mutually consistent. This assumption fails in
practice, and a growing body of work studies how to handle conflicting
evidence.

**ConflictRAG** addresses inter-document conflicts — cases where retrieved
passages contradict each other. It detects and classifies conflicts before
generation, then resolves them by ranking source credibility using an
Entropy-TOPSIS framework. The implicit assumption is that when two sources
disagree, one is more credible, and the system should identify and use it.

**TruthfulRAG** addresses a different conflict type: parametric-contextual
conflicts, where retrieved evidence contradicts the model's internal
knowledge. It builds a knowledge graph from retrieved content and uses
entropy-based filtering to identify and remove conflicting triples. Here
the assumption is that graph consistency determines truth.

**T-GRAG** addresses temporal conflicts. When a fact changes over time —
for example, a guideline updated from 2010 to 2020 — T-GRAG models the
knowledge as an evolving graph and retrieves the version appropriate to
the query's time scope. The resolution rule is recency: newer facts
supersede older ones.

**Narrative Knowledge Weaver (NKW)** is the closest work in narrative
NLP. It recognizes that narrative QA requires reasoning over dynamic
character states, causal triggers, and temporal progression, and builds a
framework that aligns textual evidence with canonical graph structure,
entity profiles, and storylines. But NKW assumes a single coherent story
world: its canonical graph presumes consistency within one narrative.

**Authority Bias in RAG** studies conflicts between user-provided
knowledge and retrieved facts. It finds that LLMs over-trust the user and
proposes a mitigation framework that favors retrieved facts over user
input. The assumption here is that user input is a factual claim that can
be wrong.

**MAGIC** is a benchmark for inter-context conflicts. It generates
synthetic conflicts by manipulating entities and relations in knowledge
graphs, and shows that both open-source and proprietary models struggle
with conflict detection, especially multi-hop reasoning. Its conflicts are
artificial and assume one source is correct.

**CONFACT** studies fact-checking under conflicting evidence from sources
of varying credibility. It introduces a dataset of questions paired with
conflicting information, and shows that incorporating media source
credibility into retrieval and generation improves conflict resolution.
Again, the assumption is a credibility hierarchy: some sources are more
reliable than others.

## The shared assumption

Across all seven works, conflict is treated as an anomaly to be
eliminated. Each proposes a mechanism to select a winner — credibility
ranking (ConflictRAG, CONFACT), graph consistency (TruthfulRAG), recency
(T-GRAG), coherence within one story world (NKW), factual correctness
over user input (Authority Bias), or synthetic ground truth (MAGIC).

What none of them consider is a domain where conflict is **permanent and
legitimate** — where multiple versions of the same fact are all valid,
and the "correct" one depends entirely on what the user asked for. In
fictional canon, the novel, the film adaptation, and the miniseries are
parallel valid branches. The user selects a branch by naming it (or by
naming its medium), and the system's job is to respect that selection,
not to override it with a universal credibility ranking.

## The gap

No existing work evaluates whether RAG systems can respect user-specified
provenance in domains where sources deliberately and permanently
contradict each other. We introduce **canon-aware retrieval** as a
specific instance of source-authority conflict in which the authoritative
source is user-determined rather than system-determined. We treat source
texts, editions, and adaptations as provenance-labeled canon branches,
and we evaluate whether retrieval systems can respect user-specified
branches and correctly surface — rather than silently merge — canon
conflict.

## Why this matters beyond fiction

The same pattern appears wherever multiple authoritative sources coexist
without a universal hierarchy: legal RAG with jurisdictional branches,
medical RAG with competing clinical guidelines, historical QA with
disputed accounts. In each case, the "correct" source is determined by
the user's context, not by a system-level ranking. Canon-aware retrieval
is a clean, information-dense test case for a problem that generalizes
well beyond fiction.
