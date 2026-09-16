import json
import re
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

RAW_DIR = Path("data/raw")
OUT_PATH = Path("data/chunks.jsonl")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " "],
    length_function=len,
)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()
    return slug[:60]


def source_type_from_branch(branch: str) -> str:
    return "comparison" if branch.endswith("_COMPARISON") else "wiki"


def main():
    files = sorted(RAW_DIR.glob("*.json"))
    print(f"Found {len(files)} raw files")

    total_chunks = 0

    with OUT_PATH.open("w", encoding="utf-8") as out:
        for path in files:
            data = json.loads(path.read_text(encoding="utf-8"))
            text = data.get("text", "")
            branch = data["branch"]
            source_type = source_type_from_branch(branch)

            if not text.strip():
                print(f"SKIP (empty): {path.name}")
                continue

            chunks = splitter.split_text(text)
            base_id = slugify(path.stem)

            for i, chunk_text in enumerate(chunks):
                record = {
                    "chunk_id": f"{base_id}_{i:04d}",
                    "text": chunk_text,
                    "branch": branch,
                    "source_type": source_type,
                    "parent_file": path.name,
                    "chunk_index": i,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                total_chunks += 1

            print(f"  {path.name}: {len(chunks)} chunks")

    print(f"\nTotal chunks: {total_chunks}")
    print(f"Written to: {OUT_PATH}")


if __name__ == "__main__":
    main()