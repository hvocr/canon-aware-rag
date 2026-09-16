import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
import trafilatura

# (domain, page_title, branch, source_type)
# page_title must be the decoded wiki title, not the URL-encoded form
WIKI_PAGES = [
    # The Shining — novel
    ("stephenking.fandom.com", "The Shining", "SHINING_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Jack Torrance", "SHINING_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Danny Torrance", "SHINING_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Wendy Torrance", "SHINING_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Dick Hallorann", "SHINING_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Overlook Hotel", "SHINING_NOVEL", "wiki"),
    ("en.wikipedia.org", "The Shining (novel)", "SHINING_NOVEL", "wiki"),

    # The Shining — Kubrick
    ("stephenking.fandom.com", "The Shining (film)", "SHINING_KUBRICK", "wiki"),
    ("stephenking.fandom.com", "Jack Torrance (films)", "SHINING_KUBRICK", "wiki"),
    ("stephenking.fandom.com", "Dick Hallorann (films)", "SHINING_KUBRICK", "wiki"),
    ("en.wikipedia.org", "The Shining (film)", "SHINING_KUBRICK", "wiki"),

    # The Shining — 1997
    ("stephenking.fandom.com", "The Shining (miniseries)", "SHINING_1997", "wiki"),
    ("en.wikipedia.org", "The Shining (miniseries)", "SHINING_1997", "wiki"),

    # The Stand — 1978
    ("stephenking.fandom.com", "The Stand", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Stuart Redman", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Frances Goldsmith", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Randall Flagg", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Abagail Freemantle", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Nick Andros", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Harold Lauder", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Nadine Cross", "STAND_NOVEL_1978", "wiki"),
    ("stephenking.fandom.com", "Donald Elbert", "STAND_NOVEL_1978", "wiki"),
    ("en.wikipedia.org", "The Stand", "STAND_NOVEL_1978", "wiki"),

    # The Stand — 1990 uncut
    ("stephenking.fandom.com", "The Stand: The Complete & Uncut Edition", "STAND_NOVEL_1990", "wiki"),
    ("stephenking.fandom.com", "The Kid", "STAND_NOVEL_1990", "wiki"),
    ("stephenking.fandom.com", "Donald Elbert", "STAND_NOVEL_1990", "wiki"),

    # The Stand — 1994
    ("stephenking.fandom.com", "The Stand (1994 Miniseries)", "STAND_1994", "wiki"),
    ("stephenking.fandom.com", "Randall Flagg", "STAND_1994", "wiki"),
    ("en.wikipedia.org", "The Stand (1994 miniseries)", "STAND_1994", "wiki"),

    # The Stand — 2020
    ("stephenking.fandom.com", "The Stand (2020 Miniseries)", "STAND_2020", "wiki"),
    ("stephenking.fandom.com", "Randall Flagg", "STAND_2020", "wiki"),
    ("en.wikipedia.org", "The Stand (2020 miniseries)", "STAND_2020", "wiki"),

    # 'Salem's Lot — novel
    ("stephenking.fandom.com", "Salem's Lot", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Ben Mears", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Kurt Barlow", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Richard Straker", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Susan Norton", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Mark Petrie", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Donald Callahan", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Mike Ryerson", "SALEMS_LOT_NOVEL", "wiki"),
    ("stephenking.fandom.com", "Matt Burke", "SALEMS_LOT_NOVEL", "wiki"),
    ("en.wikipedia.org", "'Salem's Lot", "SALEMS_LOT_NOVEL", "wiki"),

    # 'Salem's Lot — 1979
    ("stephenking.fandom.com", "Salem's Lot (1979 miniseries)", "SALEMS_LOT_1979", "wiki"),
    ("stephenking.fandom.com", "Kurt Barlow", "SALEMS_LOT_1979", "wiki"),
    ("en.wikipedia.org", "Salem's Lot (1979 miniseries)", "SALEMS_LOT_1979", "wiki"),

    # 'Salem's Lot — 2004
    ("stephenking.fandom.com", "Salem's Lot (2004 miniseries)", "SALEMS_LOT_2004", "wiki"),
    ("stephenking.fandom.com", "Kurt Barlow", "SALEMS_LOT_2004", "wiki"),
    ("en.wikipedia.org", "Salem's Lot (2004 miniseries)", "SALEMS_LOT_2004", "wiki"),

    # 'Salem's Lot — 2024
    ("stephenking.fandom.com", "Salem's Lot (film)", "SALEMS_LOT_2024", "wiki"),
    ("en.wikipedia.org", "'Salem's Lot (film)", "SALEMS_LOT_2024", "wiki"),
]

# (url, branch, source_type)
ARTICLE_URLS = [
    ("https://www.slashfilm.com/699756/why-stanley-kubrick-decided-to-scrap-the-shinings-original-ending/", "SHINING_COMPARISON", "article"),
    ("https://www.cbr.com/the-stand-biggest-differences-stephen-kings-novel/", "STAND_COMPARISON", "article"),
    ("https://allthingsfadra.com/the-stand-1994-vs-the-stand-2020/", "STAND_COMPARISON", "article"),
    ("https://www.slashfilm.com/973468/the-stand-miniseries-let-stephen-king-correct-a-major-regret/", "STAND_COMPARISON", "article"),
    ("https://www.cbr.com/salems-lot-barlow-nosferatu-similarties-mistake/", "SALEMS_LOT_COMPARISON", "article"),
    ("https://screenrant.com/salems-lot-biggest-differences-miniseries-stephen-king-book/", "SALEMS_LOT_COMPARISON", "article"),
    ("https://screenrant.com/salems-lot-movies-miniseries-ranked-worst-best/", "SALEMS_LOT_COMPARISON", "article"),
]

OUT_DIR = Path("data/raw")
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "canon-aware-rag-research/0.1 (academic corpus construction)"
}


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_")
    return slug[:180]


def fetch_wiki(domain: str, title: str):
    """Fetch a wiki page via the MediaWiki parse API, return (real_title, text)."""
    if domain.endswith("wikipedia.org"):
        url = f"https://{domain}/w/api.php"
    else:
        url = f"https://{domain}/api.php"

    params = {
        "action": "parse",
        "format": "json",
        "page": title,
        "prop": "text",
        "redirects": 1,
        "disableeditsection": 1,
        "disabletoc": 1,
    }
    resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        return None, None

    html = data.get("parse", {}).get("text", {}).get("*")
    real_title = data.get("parse", {}).get("title")

    if not html:
        return real_title, None

    text = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )
    return real_title, text

def fetch_article(url: str):
    """Fetch a regular web article, return (None, text)."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    text = trafilatura.extract(
        resp.text,
        include_comments=False,
        include_tables=False,
        favor_precision=True,
    )
    return None, text


def save(record: dict, slug: str):
    out_path = OUT_DIR / f"{slug}.json"
    out_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  SAVED: {out_path} ({len(record['text'])} chars)")


def main():
    print(f"=== Wiki pages ({len(WIKI_PAGES)}) ===")
    for domain, title, branch, source_type in WIKI_PAGES:
        slug = slugify(f"{domain}_{title}_{branch}")
        out_path = OUT_DIR / f"{slug}.json"

        if out_path.exists():
            print(f"SKIP (exists): {title} [{branch}]")
            continue

        print(f"FETCH: {title} [{branch}]")
        try:
            real_title, text = fetch_wiki(domain, title)
        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(2)
            continue

        if not text:
            print(f"  WARNING: no text (title={real_title})")
            time.sleep(2)
            continue

        record = {
            "url": f"https://{domain}/wiki/{title.replace(' ', '_')}",
            "title": real_title,
            "branch": branch,
            "source_type": source_type,
            "text": text,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        save(record, slug)
        time.sleep(2)

    print(f"\n=== Articles ({len(ARTICLE_URLS)}) ===")
    for url, branch, source_type in ARTICLE_URLS:
        slug = slugify(f"{url}_{branch}")
        out_path = OUT_DIR / f"{slug}.json"

        if out_path.exists():
            print(f"SKIP (exists): {url}")
            continue

        print(f"FETCH: {url}")
        try:
            _, text = fetch_article(url)
        except Exception as e:
            print(f"  ERROR: {e}")
            time.sleep(2)
            continue

        if not text:
            print(f"  WARNING: no text")
            time.sleep(2)
            continue

        record = {
            "url": url,
            "title": None,
            "branch": branch,
            "source_type": source_type,
            "text": text,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        save(record, slug)
        time.sleep(2)


if __name__ == "__main__":
    main()