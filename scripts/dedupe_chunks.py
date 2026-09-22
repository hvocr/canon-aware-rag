import json
from pathlib import Path

CHUNKS = Path("data/chunks.jsonl")
OUT = Path("data/chunks_dedup.jsonl")

# Prefer Fandom over Wikipedia when both exist
def prefer(ids):
    fandom = [i for i in ids if "fandom" in i]
    return fandom[0] if fandom else ids[0]


seen = {}
with CHUNKS.open(encoding="utf-8") as f:
    for line in f:
        rec = json.loads(line)
        key = rec["text"][:200]
        seen.setdefault(key, []).append(rec)

kept = []
dropped = 0
for key, records in seen.items():
    if len(records) == 1:
        kept.append(records[0])
    else:
        ids = [r["chunk_id"] for r in records]
        keep_id = prefer(ids)
        keep_rec = next(r for r in records if r["chunk_id"] == keep_id)
        kept.append(keep_rec)
        dropped += len(records) - 1

with OUT.open("w", encoding="utf-8") as f:
    for rec in kept:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

print(f"Kept {len(kept)} chunks, dropped {dropped} duplicates")
print(f"Written to: {OUT}")