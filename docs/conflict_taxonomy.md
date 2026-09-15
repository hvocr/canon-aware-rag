# Canon Conflict Taxonomy

## Purpose
A taxonomy of the ways in which facts conflict across canon branches in
the scoped works. Used for (a) constructing the query set and (b)
categorizing retrieval failures.

## Categories

### C1: Adaptation Divergence
Same event, same characters, different outcome.

Examples:
- *The Shining*: Dick Hallorann survives in `SHINING_NOVEL`, dies in
  `SHINING_KUBRICK`, survives in `SHINING_1997`.
- *The Stand*: Frannie's pregnancy outcome and the Trashcan Man's fate
  differ across `STAND_NOVEL_1990` and `STAND_1994`.
- *'Salem's Lot*: Susan Norton's fate differs across `SALEMS_LOT_NOVEL`
  and `SALEMS_LOT_1979`.

### C2: Timeline / Setting Shift
Same story, relocated in time or place.

Examples:
- *The Stand*: set in the 1990s in `STAND_NOVEL_1990`, contemporary in
  `STAND_2020`.
- *'Salem's Lot*: set in the 1970s in `SALEMS_LOT_NOVEL`, contemporary
  in `SALEMS_LOT_2004` and `SALEMS_LOT_2024`.
- *The Shining*: the Overlook's history is presented differently across
  `SHINING_NOVEL` and `SHINING_KUBRICK`.

### C3: Edition Revision / Retcon
A later edition of the same work overwrites earlier details.

Examples:
- *The Stand*: the 1990 uncut edition restores ~400 pages cut from the
  1978 edition, including the Kid and expanded Trashcan Man backstory.
  Facts about these characters do not exist in `STAND_NOVEL_1978`.

### C4: Character Redesign
Same character, incompatible traits, appearance, or behavior.

Examples:
- *'Salem's Lot*: Kurt Barlow is barely seen and animalistic in
  `SALEMS_LOT_NOVEL`, a suave human-like figure in `SALEMS_LOT_2004`,
  and a monstrous Nosferatu in `SALEMS_LOT_1979`.
- *The Shining*: Jack Torrance's characterization and descent differ
  substantially between `SHINING_NOVEL` and `SHINING_KUBRICK`.

### C5: Ending Divergence
Different resolution to the same narrative.

Examples:
- *The Shining*: the Overlook's destruction differs across
  `SHINING_NOVEL`, `SHINING_KUBRICK`, and `SHINING_1997`.
- *The Stand*: the Las Vegas climax and the fate of the main characters
  differ across `STAND_NOVEL_1990`, `STAND_1994`, and `STAND_2020`.

## Query construction

Each query in the eval set is tagged with:
- `conflict_type`: C1–C5 (or `NONE` if no conflict exists)
- `query_type`: `SPECIFIC` | `AMBIGUOUS` | `CROSSWORK`
- `branch_expected`: the correct branch for `SPECIFIC` queries
- `ground_truth`: the correct answer per branch

### Query type definitions
- `SPECIFIC`: names a branch explicitly or by medium. System must
  retrieve from that branch only.
- `AMBIGUOUS`: names no branch. System should surface the conflict
  rather than pick one silently.
- `CROSSWORK`: asks about a relation between two works. System should
  not conflate them; if no connection exists, it should say so.

## Failure categories (for error analysis)

When the baseline system fails, classify the failure as:
- **F1: Canon mixing** — answer combines facts from two or more branches.
- **F2: Branch misidentification** — answer uses the wrong branch for a
  `SPECIFIC` query.
- **F3: Silent resolution** — answer picks one branch for an `AMBIGUOUS`
  query without acknowledging the conflict.
- **F4: Cross-work conflation** — answer merges facts from two
  unrelated works.
- **F5: Fabrication** — answer states a fact not present in any branch.
