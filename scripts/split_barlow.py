import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import trafilatura

OUT_DIR = Path("data/raw")

# Section number -> branch label
BRANCH_MAP = {
    1: "SALEMS_LOT_NOVEL",   # == Salem's Lot ==
    2: "SALEMS_LOT_1979",    # === 1979 miniseries ===
    3: "SALEMS_LOT_2004",    # === 2004 miniseries ===
    4: "SALEMS_LOT_2024",    # === 2024 film ===
}

HEADERS = {"User-Agent": "canon-aware-rag-research/0.1 (academic corpus construction)"}


def fetch_section(page: str, section_num: int):
    url = "https://stephenking.fandom.com/api.php"
    params = {
        "action": "parse",
        "format": "json",
        "page": page,
        "prop": "text",
        "section": section_num,
        "redirects": 1,
        "disableeditsection": 1,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        print(f"  API error: {data['error']}")
        return None
    html = data.get("parse", {}).get("text", {}).get("*")
    if not html:
        return None
    return trafilatura.extract(
        html, include_comments=False, include_tables=False, favor_precision=True
    )


def main():
    for section_num, branch in BRANCH_MAP.items():
        print(f"FETCH: Kurt Barlow section {section_num} -> {branch}")
        try:
            text = fetch_section("Kurt Barlow", section_num)
        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(2)
            continue
        if not text:
            print(f"  WARNING: empty")
            time.sleep(2)
            continue

        slug = f"stephenking_fandom_com_Kurt_Barlow_{branch}"
        record = {
            "url": "https://stephenking.fandom.com/wiki/Kurt_Barlow",
            "title": f"Kurt Barlow (section {section_num})",
            "branch": branch,
            "source_type": "wiki",
            "text": text,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        out_path = OUT_DIR / f"{slug}.json"
        out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  SAVED: {out_path.name} ({len(text)} chars)")
        time.sleep(2)


if __name__ == "__main__":
    main()