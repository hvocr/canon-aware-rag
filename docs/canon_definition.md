# Operational Definition of Canon

## Purpose
This document defines "canon" as used in this project. It is a working
definition for retrieval research, not a claim about which version of a
story is authoritative.

## Definition

We define canon operationally as a **provenance label** attached to each
retrieved chunk, indicating the specific source text, edition, or
adaptation from which the fact originates.

We do not adjudicate which branch is "authoritative" or "true." A fact is
canon-correct **relative to a specified branch**, not absolutely.

A query is **canon-specified** if it names a branch explicitly (e.g., "in
the 1997 miniseries") or by medium (e.g., "in the Kubrick film"). A query
is **canon-ambiguous** if it names no branch and the fact in question
differs across branches.

## Branch labels

### The Shining
- `SHINING_NOVEL` — Stephen King, *The Shining* (1977)
- `SHINING_KUBRICK` — Stanley Kubrick, *The Shining* (1980)
- `SHINING_1997` — Mick Garris, ABC miniseries (1997)

### The Stand
- `STAND_NOVEL_1978` — Stephen King, *The Stand* (1978, original edition)
- `STAND_NOVEL_1990` — Stephen King, *The Stand* (1990, uncut edition)
- `STAND_1994` — Mick Garris, ABC miniseries (1994)
- `STAND_2020` — CBS All Access miniseries (2020)

### 'Salem's Lot
- `SALEMS_LOT_NOVEL` — Stephen King, *'Salem's Lot* (1975)
- `SALEMS_LOT_1979` — Tobe Hooper, CBS miniseries (1979)
- `SALEMS_LOT_2004` — Mikael Salomon, TNT miniseries (2004)
- `SALEMS_LOT_2024` — Gary Dauberman, film (2024)

## Rules

1. Every chunk in the corpus receives exactly one branch label.
2. A chunk that discusses multiple branches receives the label of the
   branch it primarily describes. Multi-branch chunks are flagged
   `MULTI` and excluded from single-branch retrieval experiments.
3. Paratext (author's notes, interviews, adaptation commentary) is
   labeled `META` and excluded from the eval set.
4. Comparison articles that explicitly discuss divergences are labeled
   `COMPARISON` and treated as a separate retrieval source.

## What this definition excludes

- Fan theories, headcanon, and wiki speculation pages.
- Cross-work connections (e.g., references to other King works) unless
  the chunk explicitly states the connection and its branch.
- Comic, stage, and radio adaptations.
- Doctor Sleep and The Dark Tower (out of scope).

## Why this matters for retrieval

Standard RAG assigns no provenance to retrieved chunks. When a user asks
about a fact that differs across branches, a provenance-blind system will
retrieve and merge chunks from multiple branches, producing an answer
that is correct in no single branch. Canon-aware retrieval uses the
branch label to constrain or weight retrieval.
