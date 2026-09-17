# Framing: Provenance Arbitration

## The problem

RAG systems retrieve passages from a knowledge base and generate answers.
When retrieved passages conflict, the system must decide what to do.
Prior work treats this as **conflict resolution**: determine which source
is correct (ConflictRAG), or abstain when no source dominates (ConRAG).

We argue this framing is wrong for a class of domains we call
**parallel-valid canon domains**, where multiple versions of the same
fact are all legitimate and the "correct" one depends on what the user
asked for.

## The reframing

We frame the problem as **provenance arbitration**: the system must
decide which source is authoritative **for this query**, where authority
is determined by the user, not by the system.

Two arbitration modes:

| Mode | Who decides authority | Example |
|---|---|---|
| **System-determined** | Credibility, recency, graph consistency | ConflictRAG, T-GRAG |
| **User-determined** | The user's provenance specification | This work |

System-determined arbitration assumes a universal authority hierarchy.
User-determined arbitration assumes authority is context-dependent.

## Why system arbitration fails in canon domains

In fact-checking (FEVER, SciFact), a credibility ranking works: the
peer-reviewed source beats the blog post. In fiction canon, there is no
hierarchy. The novel is not more authoritative than the film. The 1990
uncut edition is not more authoritative than the 1978 original. They
are **parallel branches**, each valid within its own scope.

A system that applies credibility ranking to canon will silently pick
one branch and present its answer as fact. This is wrong not because
the answer is incorrect, but because **the user's provenance
specification was ignored**.

## Three arbitration regimes

We evaluate three cases:

1. **Explicit specification** — user names the branch.
   Query: "Does Hallorann survive in the novel?"
   Correct behavior: retrieve from NOVEL only.

2. **Implicit specification** — user describes the branch without
   naming it.
   Query: "In the version where Jack is a loving father, does
   Hallorann survive?"
   Correct behavior: infer NOVEL branch, retrieve from it.

3. **No specification** — user does not indicate a branch.
   Query: "Does Hallorann survive The Shining?"
   Correct behavior: surface the conflict, present per-branch answers.

System-determined arbitration collapses all three into one behavior.
User-determined arbitration requires distinguishing them.

## Contribution

We formalize user-determined provenance arbitration, introduce a
provenance-annotated benchmark for two franchises, and measure how
often baseline RAG systems fail to respect user-specified provenance.

## Relation to prior work

- **ConflictRAG**: system-determined arbitration via credibility ranking.
- **ConRAG**: system-determined arbitration via stance adjudication and
  abstention (NEI) under conflict.
- **TruthfulRAG**: system-determined arbitration via knowledge graph
  consistency.
- **T-GRAG**: system-determined arbitration via recency.
- **This work**: user-determined arbitration via provenance specification.
