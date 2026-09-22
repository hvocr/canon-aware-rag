# Data Limitations

## Source conflicts during verification

- **ST-007/ST-008 (Nick Andros' ghost appearance):** The CBR article
  states the 2020 adaptation omits the spectral Nick; the Wikipedia
  2020 page states the character appears as a ghost and speaks. We
  could not resolve this conflict and removed the seed facts and
  associated queries from the dataset.

- **SL-017/SL-018 (Father Callahan's role in 1979):** ScreenRant
  describes Callahan as a "severely reduced minor character" in the
  1979 miniseries, but Callahan does not appear in the 1979 corpus.
  We removed the associated queries (Q107, Q108).

## Corpus size imbalance

  Chunk counts vary substantially across canon branches:

  - SHINING_KUBRICK: 98
  - STAND_NOVEL_1978: 81
  - SHINING_NOVEL: 48
  - ... (down to)
  - STAND_NOVEL_1990: 5
  - SHINING_COMPARISON: 4

  This imbalance is realistic — real corpora are not uniformly distributed
  — but it affects retrieval: baseline systems may bias toward branches
  with more chunks, regardless of query intent. We report per-branch
  results and acknowledge that thin branches (fewer than 15 chunks) may
  produce artificially high filtered accuracy due to the small retrieval
  pool.