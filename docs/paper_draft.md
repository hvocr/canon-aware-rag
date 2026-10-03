# Canon-Aware Retrieval: User-Determined Provenance Arbitration in Parallel-Valid Fiction Domains

## Abstract

Retrieval-Augmented Generation (RAG) systems implicitly assume that retrieved passages are mutually consistent. This assumption fails in domains where multiple authoritative versions of the same fact coexist without a hierarchy — legal jurisdictions, competing clinical guidelines, historical disputes, and fiction canon. Prior work on conflict-aware RAG resolves such conflicts by selecting a winner (via credibility, recency, graph consistency) or by adjudicating a stance and abstaining under uncertainty. We study a different problem: user-determined provenance arbitration, in which the authoritative source is specified by the user, not determined by the system. We introduce a provenance-annotated benchmark of 43 canon conflicts and 124 evaluation queries across three Stephen King works and their adaptations, with inter-annotator agreement of kappa = 0.85. We evaluate four retrieval variants: a vanilla RAG baseline, keyword-based branch filtering, LLM-based branch classification, and classifier-plus-per-branch retrieval. Our results show that branch-aware retrieval nearly eliminates cross-branch retrieval on explicit queries (0.46 to 0.98 retrieval precision), but that LLM-based classification over-commits on ambiguous queries (conflict surfacing regresses from 16/24 to 13/24), and that per-branch retrieval recovers ambiguous performance (13/24 to 20/24) at the cost of implicit-query precision (0.54 to 0.41). A per-branch analysis reveals that these gains are concentrated in under-represented branches, correcting a dominance bias in vanilla retrieval. No single variant dominates. Branch-aware retrieval requires recognizing both when a user names a branch and when they do not — two capabilities that are in tension.

## 1. Introduction

Retrieval-Augmented Generation grounds large language model outputs in external knowledge, reducing hallucination and enabling knowledge-intensive tasks. The core pipeline retrieves relevant passages and conditions generation on them. This pipeline implicitly assumes that retrieved passages are mutually consistent: that if two passages describe the same fact, they agree.

This assumption fails frequently. In legal RAG, jurisdictional branches state contradictory rules. In medical RAG, competing clinical guidelines recommend different treatments. In fact-checking, sources of varying credibility assert incompatible claims. In each case, a system that concatenates retrieved passages will produce an answer that silently merges contradiction.

A growing body of work addresses this. ConflictRAG detects and classifies conflicts and resolves them by ranking source credibility. TruthfulRAG resolves conflicts via knowledge graph consistency. T-GRAG models temporal conflict and applies recency as a resolution rule. ConRAG makes conflict explicit through an evidence table but still adjudicates a correct stance and abstains when evidence is balanced. Across these works, conflict is treated as an anomaly to be eliminated — the system determines which source is authoritative.

We study a domain where this framing is wrong. In fictional canon, multiple versions of the same story are all legitimate. The novel and the film are not competing claims about a single world; they are parallel valid branches. The correct source is determined by what the user asked for, not by credibility, recency, or graph consistency. We call this user-determined provenance arbitration.

We make three contributions:

1. A reframing. We formalize the distinction between system-determined arbitration (prior work) and user-determined arbitration (this work), and identify parallel-valid canon domains as a clean test case for the latter.

2. A benchmark. We release a provenance-annotated corpus of 436 chunks across 11 canon branches, a seed fact table of 43 verified canon conflicts, and 124 evaluation queries across four types (EXPLICIT, IMPLICIT, AMBIGUOUS, CONTROL), with inter-annotator agreement of kappa = 0.85.

3. A measurement. We evaluate four retrieval variants on this benchmark and characterize where branch-aware retrieval succeeds and where it fails, showing that explicit-branch handling and ambiguous-branch handling are in tension, and that the gains concentrate in branches that are under-represented in the underlying corpus.

## 2. Related Work

### 2.1 Conflict-Aware RAG

ConflictRAG addresses inter-document conflicts — cases where retrieved passages contradict each other. It detects and classifies conflicts before generation, then resolves them by ranking source credibility using an Entropy-TOPSIS framework. The implicit assumption is that when two sources disagree, one is more credible.

TruthfulRAG addresses parametric-contextual conflicts, where retrieved evidence contradicts the model's internal knowledge. It builds a knowledge graph from retrieved content and applies entropy-based filtering to identify and remove conflicting triples. Graph consistency determines truth.

T-GRAG addresses temporal conflicts. It models knowledge as an evolving graph and retrieves the version appropriate to the query's time scope. The resolution rule is recency.

ConRAG makes multi-source disagreement explicit rather than silently merging it. It tags passages as Support, Refute, or Irrelevant, clusters them into consistent evidence groups, and computes a conflict score. When disagreement is high, it preserves both sides and generates an answer with an explicit stance (Support / Refute / NotEnoughInfo) and sentence-level citations. However, ConRAG still adjudicates a correct stance and abstains when evidence is balanced — it assumes a single ground truth exists even when the system cannot determine it.

Authority Bias in RAG studies conflicts between user-provided knowledge and retrieved facts, finding that LLMs over-trust the user and proposing a mitigation framework that favors retrieved facts. The assumption is that user input is a factual claim that can be wrong.

MAGIC is a benchmark for inter-context conflicts, generating synthetic conflicts by manipulating entities and relations in knowledge graphs. Conflicts are artificial and assume one source is correct.

CONFACT studies fact-checking under conflicting evidence from sources of varying credibility, and shows that incorporating media source credibility improves conflict resolution. Again, the assumption is a credibility hierarchy.

ConfRAG is a benchmark for evaluating LLM reasoning over conflicting web references, containing 1,814 questions of which 57 percent contain explicit contradictions. It measures answer clustering and coverage but does not propose a retrieval method.

### 2.2 Narrative-Aware Retrieval

Narrative Knowledge Weaver (NKW) recognizes that narrative QA requires reasoning over dynamic character states and causal triggers, and builds a framework aligning textual evidence with canonical graph structure, entity profiles, and storylines. However, NKW assumes a single coherent story world — its canonical graph presumes consistency within one narrative.

### 2.3 The shared assumption

Across all prior works, conflict is treated as an anomaly to be eliminated. Each proposes a mechanism to select a winner: credibility ranking (ConflictRAG, CONFACT), graph consistency (TruthfulRAG), recency (T-GRAG), coherence within one story world (NKW), factual correctness over user input (Authority Bias), or synthetic ground truth (MAGIC). ConRAG advances the field by making conflict explicit rather than silently merging it, but still adjudicates a stance.

None treats the user as a legitimate provenance selector in a domain where all branches are equally valid.

### 2.4 Positioning

We frame this problem as provenance arbitration: deciding which source is authoritative for a query, where authority is determined by the user rather than by the system. Prior work performs system-determined arbitration. We study user-determined arbitration in parallel-valid canon domains, where no universal hierarchy exists and the user's provenance specification determines the correct answer.

The same pattern appears wherever multiple authoritative sources coexist without a universal hierarchy: legal RAG with jurisdictional branches, medical RAG with competing guidelines, historical QA with disputed accounts. Canon-aware retrieval is a clean, information-dense test case for a problem that generalizes beyond fiction.

## 3. Framing: Provenance Arbitration

### 3.1 Two arbitration modes

We distinguish two ways a system can decide which source is authoritative for a query.

System-determined arbitration. The system decides. It ranks sources by credibility (ConflictRAG, CONFACT), recency (T-GRAG), graph consistency (TruthfulRAG), or adjudicates a stance and abstains under uncertainty (ConRAG). This assumes a universal authority hierarchy exists or can be inferred.

User-determined arbitration. The user decides. The system's role is to respect the user's provenance specification rather than override it. Authority is context-dependent.

### 3.2 Three arbitration regimes

We evaluate three cases:

1. Explicit specification. The user names the branch ("in the novel", "in the 1979 miniseries", "Kubrick's film"). Correct behavior: retrieve from that branch only.

2. Implicit specification. The user describes the branch by a distinctive trait without naming it ("in the version where Jack freezes in the hedge maze"). Correct behavior: infer the branch from the description, then retrieve from it.

3. No specification. The user names no branch and describes none ("Does Hallorann survive The Shining?"). Correct behavior: surface the conflict, present per-branch answers.

System-determined arbitration collapses all three into one behavior. User-determined arbitration requires distinguishing them.

### 3.3 Conflict taxonomy

We define five categories of canon conflict, used to construct the seed fact table and to categorize failures:

C1: Adaptation divergence. Same event, different outcome across versions. Example: Dick Hallorann survives in the novel and dies in Kubrick's film.

C2: Timeline / setting shift. Same story, relocated. Example: The Stand is set in the 1990s in the 1990 uncut edition and in the modern day in the 2020 miniseries.

C3: Edition revision / retcon. A later edition overwrites earlier details. Example: The Kid appears only in the 1990 uncut edition of The Stand.

C4: Character redesign. Same character, incompatible traits. Example: Kurt Barlow is human-looking in the novel, Nosferatu-like in the 1979 miniseries, a sophisticated gentleman in 2004, and Nosferatu-like again in 2024.

C5: Ending divergence. Different resolution. Example: Jack Torrance dies in a boiler explosion in the novel and freezes in a hedge maze in the film.

## 4. Method

### 4.1 Corpus

We construct a provenance-annotated corpus across three Stephen King works and their adaptations: The Shining (novel 1977, Kubrick film 1980, 1997 miniseries), The Stand (original 1978 edition, 1990 uncut edition, 1994 miniseries, 2020 miniseries), and Salem's Lot (novel 1975, 1979 miniseries, 2004 miniseries, 2024 film). Eleven canon branches total.

Sources are secondary: Fandom wiki pages, Wikipedia plot summaries, and comparison articles from CBR, ScreenRant, SlashFilm, and Polygon. No primary novel or script text is used. Sources are fetched via the MediaWiki parse API for wikis and via direct HTML extraction for articles. Character pages with per-branch sections (e.g., Kurt Barlow) are split at the section level; pages without per-branch structure are retained under the novel branch only and noted as a limitation.

After deduplication, the corpus contains 436 chunks with an average length of approximately 350 tokens. Chunk counts vary substantially across branches, ranging from 4 to 98 chunks.

### 4.2 Seed fact table

We manually construct a seed fact table of 43 verified canon conflicts, each labeled with a work, event, branch, fact value, and conflict type (C1 to C5). All facts are verified against the corpus. Facts where sources conflict irreconcilably (for example, conflicting accounts of Nick Andros's spectral appearance in the 2020 Stand miniseries) are removed and recorded as a limitation.

### 4.3 Query set

We generate 124 evaluation queries from the seed fact table using an LLM-assisted pipeline, with manual verification against the corpus. Queries fall into four types:

- EXPLICIT (41): the query names a branch.
- IMPLICIT (38): the query describes a branch without naming it.
- AMBIGUOUS (24): the query names no branch and describes none.
- CONTROL (21): the query has the same answer across all branches.

Ground truths for EXPLICIT and IMPLICIT queries are programmatically verified against the corpus via keyword matching, with manual review of flagged cases. AMBIGUOUS query ground truths list per-branch answers and are manually verified. CONTROL query ground truths are stable facts (character identities, authorship, stable plot elements).

### 4.4 Inter-annotator agreement

Two annotators independently labeled a stratified sample of 30 queries (10 EXPLICIT, 10 IMPLICIT, 10 AMBIGUOUS) into the four query types. Raw agreement was 90.0 percent (27/30). Cohen's kappa was 0.850, indicating almost perfect agreement. All disagreements occurred on queries where a branch was described by a distinctive trait without explicit naming (the IMPLICIT/AMBIGUOUS boundary).

### 4.5 Retrieval pipeline

Embeddings: BAAI/bge-small-en-v1.5, normalized, cosine similarity.

Vector store: ChromaDB with metadata filtering on branch labels.

Reranker: cross-encoder/ms-marco-MiniLM-L-6-v2. Retrieval returns top-20; reranking returns top-5.

Generator: Groq's openai/gpt-oss-120b, temperature 0.0, max 1500 tokens.

### 4.6 Variants

Vanilla (baseline). No branch awareness. Retrieval top-20, rerank top-5, standard generation prompt.

B1 (Keyword). A keyword dictionary maps surface tokens ("novel", "1979", "Kubrick") to branch labels. If a keyword matches, retrieval is filtered to that branch; otherwise global retrieval. Reranking and generation as baseline.

B2 (Classifier). An LLM classifies each query into one of the 11 branches or NONE. Filtered retrieval when a branch is identified; global retrieval otherwise. Reranking and generation as baseline.

B3 (Classifier + Per-Branch). Uses B2's classifier. When a branch is identified, behaves identically to B2. When no branch is identified, retrieves the top-3 chunks from every branch (33 candidates), reranks to top-10, and prompts the generator to answer per-branch with a structured bullet list.

## 5. Results

### 5.1 Main results

Table 1 reports retrieval precision (fraction of top-5 chunks from the expected branch, for EXPLICIT and IMPLICIT queries) and conflict surfacing (fraction of AMBIGUOUS queries where the answer mentions at least two distinct versions).

Table 1: Main results.

| Variant | EXPLICIT RetrPrec | IMPLICIT RetrPrec | AMBIGUOUS ConflictSurfaced |
|---|---|---|---|
| Vanilla | 0.46 | 0.41 | 16/24 |
| B1: Keyword | 0.54 | 0.39 | 19/24 |
| B2: Classifier | 0.98 | 0.54 | 13/24 |
| B3: Classifier + PB | 0.97 | 0.41 | 20/24 |

### 5.2 Finding 1: Branch classification nearly solves explicit retrieval

EXPLICIT retrieval precision rises from 0.46 (Vanilla) to 0.98 (B2). When the user names a branch, LLM-based classification almost always identifies it correctly, and branch filtering retrieves almost exclusively from that branch. Keyword matching (B1) achieves only 0.54 because keyword collisions across works (the word "novel" appears in queries about all three works) cause frequent misclassification.

### 5.3 Finding 2: Classification over-commits on ambiguous queries

B2 regresses on AMBIGUOUS conflict surfacing relative to Vanilla (16/24 to 13/24). The classifier returns a branch label for some ambiguous queries, whereupon retrieval is filtered to that branch and the generator no longer sees other versions. The mechanism that fixes EXPLICIT breaks AMBIGUOUS: branch classification has no "I don't know" threshold tuned for ambiguous input.

### 5.4 Finding 3: Per-branch retrieval recovers ambiguous performance

B3 recovers AMBIGUOUS conflict surfacing to 20/24, above both Vanilla (16/24) and B2 (13/24). When no branch is identified, retrieving top-3 per branch guarantees that the generator sees multiple versions, and the per-branch prompt elicits explicit per-branch answers.

### 5.5 Finding 4: A trade-off between explicit and implicit handling

B3's IMPLICIT retrieval precision drops from 0.54 (B2) to 0.41. IMPLICIT queries do not name a branch, so the classifier is more likely to return NONE, triggering B3's per-branch fallback. The fallback retrieves from all branches rather than the intended one, so branch-consistent chunks are diluted. Explicit handling and implicit handling are in tension: per-branch fallback helps ambiguous queries but hurts implicit ones.

### 5.6 Per-branch analysis

The aggregate EXPLICIT precision of 0.46 (Vanilla) masks wide per-branch variation. Table 2 reports retrieval precision per branch, sorted by corpus size.

Table 2: Per-branch retrieval precision (EXPLICIT and IMPLICIT queries only).

| Branch | Chunks | Queries | Vanilla | B2 | Delta |
|---|---|---|---|---|---|
| SHINING_KUBRICK | 98 | 15 | 0.75 | 0.72 | -0.03 |
| STAND_NOVEL_1978 | 81 | 6 | 0.23 | 0.83 | +0.60 |
| SHINING_NOVEL | 48 | 15 | 0.49 | 0.76 | +0.27 |
| SALEMS_LOT_NOVEL | 42 | 16 | 0.49 | 0.86 | +0.37 |
| STAND_1994 | 32 | 2 | 0.60 | 1.00 | +0.40 |
| SALEMS_LOT_1979 | 24 | 7 | 0.29 | 0.77 | +0.48 |
| SHINING_1997 | 14 | 2 | 0.20 | 1.00 | +0.80 |
| SALEMS_LOT_2004 | 12 | 7 | 0.14 | 0.57 | +0.43 |
| STAND_2020 | 11 | 4 | 0.25 | 0.55 | +0.30 |
| STAND_NOVEL_1990 | 5 | 5 | 0.16 | 0.80 | +0.64 |

We identify a dominance bias in vanilla retrieval. Branches with more chunks about a query topic dominate retrieval regardless of the branch the user asked about. STAND_NOVEL_1978 (81 chunks, second largest) achieves only 0.23 precision in vanilla because comparison-article chunks covering the same topics dominate retrieval. SALEMS_LOT_2004 achieves 0.14; STAND_NOVEL_1990 achieves 0.16.

Branch classification (B2) corrects this for every under-represented branch. Gains range from +0.27 to +0.80. However, the effect is not uniform. SHINING_KUBRICK (98 chunks, largest branch) shows no improvement (0.75 to 0.72), because vanilla retrieval already over-represents it. Branch-aware retrieval is therefore most valuable for branches that are under-represented relative to the dominant branch, not uniformly across branches.

This per-branch analysis is essential for interpreting the aggregate metrics. The improvement in aggregate EXPLICIT precision from 0.46 to 0.98 is largely attributable to correcting the dominance bias. A system that appears to perform uniformly well may be trivially succeeding on thin branches and struggling on thick ones. We report per-branch results in all subsequent analyses.

Branches with fewer than 20 chunks (STAND_NOVEL_1990, STAND_2020, SALEMS_LOT_2004, SHINING_1997) are represented by only 2 to 7 queries each; per-branch estimates for these branches should be treated as preliminary.

### 5.7 Qualitative examples

Example 1: Silent resolution (Vanilla). Query Q019: "How does Jack Torrance die?" Vanilla retrieved mixed branches and answered with the novel's boiler explosion as fact, without acknowledging the Kubrick film's freezing death. B3 answered with both versions in a structured list.

Example 2: Hallucination (Vanilla). Query Q074: "What happens to Father Callahan in the 2004 adaptation?" Vanilla answered that the character was played by James Cromwell. The 2004 miniseries cast James Gallery. This hallucination is not attributable to retrieval — the correct chunk was retrieved — and reflects instability in the generator.

Example 3: Retrieval contamination (B2). Query Q017: "How does Jack Torrance die in the novel of The Shining?" B2 correctly classified the query as SHINING_NOVEL but retrieved a chunk from the Kubrick wiki page that describes the novel's ending as a contrast. The chunk was not labeled SHINING_NOVEL and was excluded by filtering. Branch filtering can exclude chunks that contain the correct answer.

Example 4: Structured per-branch answer (B3). Query Q005: "Does Dick Hallorann survive The Shining?" B3 returned a three-bullet answer distinguishing SHINING_NOVEL (survives), SHINING_KUBRICK (dies), and SHINING_1997 (survives). The same query under Vanilla produced a confused single-version answer.

## 6. Error Analysis

We categorize observed failures into five types, extended from our conflict taxonomy:

F1: Canon mixing. The answer combines facts from multiple branches without acknowledgment.

F2: Branch misidentification. The answer uses the wrong branch for an EXPLICIT query.

F3: Silent resolution. The answer picks one branch for an AMBIGUOUS query without surfacing the conflict.

F4: Cross-work conflation. The answer merges facts from two unrelated works.

F5: Fabrication. The answer asserts a fact not present in any branch.

Additional failure modes observed:

Empty responses. The generator (a reasoning model) exhausted its token budget on internal reasoning, producing no output. We count these as incorrect.

Spurious citation markers. The generator occasionally appended markers such as bracketed source references that do not correspond to source chunks. These did not affect answer correctness but indicate formatting instability.

Retrieval contamination. Chunks labeled for one branch often describe another, particularly in comparison articles and wiki pages that discuss multiple versions. This limits the effectiveness of metadata-only branch filtering.

## 7. Threats to Validity

Internal validity. Ground truths for EXPLICIT and IMPLICIT queries were programmatically verified against the corpus, but per-branch sample sizes are small for some branches (2 to 7 queries). Aggregate metrics are dominated by the branches with the most queries (SHINING_NOVEL, SHINING_KUBRICK, SALEMS_LOT_NOVEL). Inter-annotator agreement was computed on 30 queries; a larger sample would refine estimates.

External validity. We evaluate on three Stephen King works only. Whether the findings transfer to other franchises (Marvel, Star Wars, Sherlock Holmes) or to non-fiction parallel-source domains (legal, medical, historical) is a hypothesis, not a demonstrated result. The corpus is small relative to production RAG systems.

Construct validity. Retrieval precision measures whether retrieved chunks come from the expected branch, but does not measure whether they contain the answer. A chunk from the correct branch may not contain the relevant fact, and a chunk from the wrong branch may. The dominance-bias finding and the retrieval-contamination finding are both consequences of this limitation.

## 8. Reproducibility and Ethics

Code and data. All scraping scripts, chunking scripts, retrieval pipelines, evaluation scripts, and scoring scripts are available in the project repository. The corpus, seed fact table, query set, and results files are included. Fandom wiki content is used under CC-BY-SA; Wikipedia content under CC-BY-SA. We do not redistribute primary novel or screenplay text.

Human subjects. This work does not involve human subjects. The inter-annotator agreement study used two annotators (one author and one volunteer) on publicly available queries; no personal data was collected.

Compute. All experiments ran on a single consumer laptop with an NVIDIA GTX 1650 Ti GPU (4 GB VRAM) and a free-tier API. No proprietary compute was used.

## 9. Limitations

Corpus size and imbalance. Chunk counts vary substantially across branches (4 to 98). Thin branches may produce artificially high filtered accuracy due to the small retrieval pool. We report per-branch results to make this visible.

Single generator. Results are from a single generator (openai/gpt-oss-120b). Whether findings transfer to other models is untested.

Corpus contamination. Sources that describe multiple versions (comparison articles, some wiki pages) label chunks with a single branch even when content spans branches. This affects retrieval precision and is a known limitation of metadata-only filtering.

Annotation sample size. Inter-annotator agreement was computed on 30 queries. Disagreements concentrated on the IMPLICIT/AMBIGUOUS boundary; expanding the sample would refine these estimates.

Domain specificity. We evaluate on Stephen King adaptations only. Generalization to other franchises and to non-fiction parallel-source domains is a hypothesis, not a demonstrated result.

## 10. Conclusion

We introduced user-determined provenance arbitration as a distinct problem from the conflict resolution studied in prior RAG work. We constructed a provenance-annotated benchmark of 43 canon conflicts and 124 queries across three Stephen King works, and evaluated four retrieval variants. Branch-aware retrieval nearly eliminates cross-branch retrieval for explicit queries (0.46 to 0.98), but the same classifier over-commits on ambiguous queries (conflict surfacing 16/24 to 13/24). Per-branch retrieval recovers ambiguous performance (13/24 to 20/24) at the cost of implicit-query precision (0.54 to 0.41). A per-branch analysis reveals that gains concentrate in under-represented branches, correcting a dominance bias in vanilla retrieval but leaving the dominant branch unchanged.

The contribution is architectural: branch-aware retrieval requires both recognizing when a user names a branch and recognizing when they do not — capabilities that pull in opposite directions under a single classifier. Future work should investigate a two-stage architecture that explicitly disambiguates between "the user specified a branch" and "the user did not," and that treats the ambiguous case as a distinct retrieval task rather than a fallback. The benchmark is a first step toward evaluating provenance-aware retrieval in domains where multiple authoritative sources coexist without a hierarchy.

## References

1. Chenyu Wang, Yingmin Liu, Yang Shu. ConflictRAG: Detecting and Resolving Knowledge Conflicts in Retrieval-Augmented Generation.

2. Shuyi Liu, Yuming Shang, Xi Zhang. TruthfulRAG: Resolving Factual-level Conflicts in Retrieval-Augmented Generation with Knowledge Graphs. arXiv:2511.10375, 2025.

3. Dong Li, Yichen Niu, Ying Ai, Xiang Zou, Biqing Qi, Jianxing Liu. T-GRAG: A Dynamic GraphRAG Framework for Resolving Temporal Conflicts and Redundancy in Knowledge Retrieval. ACM, 2025.

4. Qiuyu Tian et al. Narrative Knowledge Weaver: Narrative-Centric Retrieval-Augmented Reasoning for Long-Form Text Understanding. arXiv:2606.05724, 2026.

5. ConRAG: Contradiction-Aware Retrieval-Augmented Generation. Journal of Advanced Computing Systems, 4(7), 2024.

6. Yuxuan Li et al. LLMs Trust Humans More, That's a Problem! Unveiling and Mitigating the Authority Bias in Retrieval-Augmented Generation. ACL 2025.

7. Jungyeon Lee, Lee Kangmin, Taeuk Kim. MAGIC: A Multi-Hop and Graph-Based Benchmark for Inter-Context Conflicts in Retrieval-Augmented Generation. Findings of EMNLP 2025.

8. Ziyu Ge, Yuhao Wu, Daniel Wai Kit Chin, Roy Ka-Wei Lee, Rui Cao. Resolving Conflicting Evidence in Automated Fact-Checking: A Study on Retrieval-Augmented LLMs. IJCAI 2025.

9. ConfRAG: Benchmarking LLM's Capability in Reasoning over Conflicting Web References. ACL 2026.

10. Patrick Lewis et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.

11. Nils Reimers, Iryna Gurevych. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP 2019.