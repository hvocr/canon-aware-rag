import re
import json
from datetime import datetime, timezone
from pathlib import Path
import requests

HEADERS = {"User-Agent": "canon-aware-rag-research/0.1 (academic corpus construction)"}
OUT_DIR = Path("data/raw")


def fetch_wikitext(page: str) -> str:
    url = "https://stephenking.fandom.com/api.php"
    params = {"action": "parse", "format": "json", "page": page,
              "prop": "wikitext", "redirects": 1}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()["parse"]["wikitext"]["*"]


def strip_wiki_markup(text: str) -> str:
    text = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"'''?", "", text)
    text = re.sub(r"<ref.*?</ref>", "", text, flags=re.S)
    text = re.sub(r"\{\{.*?\}\}", "", text, flags=re.S)
    return text.strip()


wt = fetch_wikitext("Kurt Barlow")

# Split on level-2 and level-3 headings
parts = re.split(r"^(==+.*?==+)\s*$", wt, flags=re.M)

sections = {"LEAD": parts[0]}
for i in range(1, len(parts), 2):
    heading = parts[i].strip("= ").strip()
    body = parts[i + 1] if i + 1 < len(parts) else ""
    sections[heading] = body

BRANCH_MAP = {
    "LEAD": "SALEMS_LOT_NOVEL",
    "Salem's Lot": "SALEMS_LOT_NOVEL",
    "1979 miniseries": "SALEMS_LOT_1979",
    "2004 miniseries": "SALEMS_LOT_2004",
    "2024 film": "SALEMS_LOT_2024",
}

for heading, branch in BRANCH_MAP.items():
    raw = sections.get(heading, "")
    if not raw.strip():
        print(f"EMPTY: {heading}")
        continue
    text = strip_wiki_markup(raw)

    # Strip cross-branch contamination from the novel section
    if branch == "SALEMS_LOT_NOVEL":
        text = re.split(r"In Salem's Lot \(1979\)|In the 2004 miniseries", text)[0].strip()

    # Strip Dark Tower references from all sections
    text = re.sub(r"In (The Dark Tower|the Dark Tower)[^.]*\.", "", text).strip()

    slug = f"stephenking_fandom_com_Kurt_Barlow_{branch}"
    record = {
        "url": "https://stephenking.fandom.com/wiki/Kurt_Barlow",
        "title": f"Kurt Barlow ({heading})",
        "branch": branch,
        "source_type": "wiki",
        "text": text,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
    (OUT_DIR / f"{slug}.json").write_text(
        json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"SAVED {branch}: {len(text)} chars")