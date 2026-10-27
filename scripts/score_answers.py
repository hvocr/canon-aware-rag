import csv
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
GROQ_MODEL = "openai/gpt-oss-120b"

VARIANTS = {
    "vanilla": "data/results_baseline.jsonl",
    "b1": "data/results_variant_a.jsonl",
    "b2": "data/results_variant_a2.jsonl",
    "b3": "data/results_variant_c2.jsonl",
    "retrieval_only": "data/results_ablation_retrieval_only.jsonl",
    "prompt_only": "data/results_ablation_prompt_only.jsonl",
    "control": "data/results_control.jsonl",
}

with open("data/queries.csv", encoding="utf-8") as f:
    QUERIES = {r["query_id"]: r for r in csv.DictReader(f)}


def load_results(path):
    with open(path, encoding="utf-8") as f:
        return {json.loads(l)["query_id"]: json.loads(l) for l in f}


def judge(question, ground_truth, answer, query_type):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    if query_type == "AMBIGUOUS":
        instruction = (
            "The question is AMBIGUOUS. The correct answer must surface that "
            "different versions give different answers. Score 1 if the answer "
            "mentions at least two versions with their outcomes. Score 0 if it "
            "picks one version without acknowledging others."
        )
    elif query_type == "CONTROL":
        instruction = (
            "This is a CONTROL question — the answer is the same across all "
            "versions. Score 1 if the answer contains the key fact. Score 0 "
            "otherwise."
        )
    else:
        instruction = (
            "Score 1 if the answer contains the key fact from the ground truth. "
            "Score 0 if it contradicts, omits, or fabricates facts."
        )

    prompt = (
        f"{instruction}\n\n"
        f"Question: {question}\n"
        f"Ground truth: {ground_truth}\n"
        f"Answer: {answer}\n\n"
        "Respond with only '1' or '0'."
    )

    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=1500,
    )
    out = resp.choices[0].message.content.strip()
    return 1 if out.startswith("1") else 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in VARIANTS:
        print("Usage: python scripts/score_answers.py [vanilla|b2|b3]")
        return

    variant = sys.argv[1]
    results = load_results(VARIANTS[variant])
    out_path = Path(f"data/answer_scores_{variant}.jsonl")

    done = set()
    if out_path.exists():
        with out_path.open(encoding="utf-8") as f:
            for line in f:
                try:
                    done.add(json.loads(line)["query_id"])
                except Exception:
                    pass

    print(f"Variant: {variant} | Already judged: {len(done)}")

    with out_path.open("a", encoding="utf-8") as out:
        for qid, rec in results.items():
            if qid in done or qid not in QUERIES:
                continue
            q = QUERIES[qid]
            try:
                s = judge(q["query_text"], q["ground_truth"], rec["answer"], q["query_type"])
            except Exception as e:
                print(f"  {qid}: ERROR {e}")
                continue
            out.write(json.dumps({
                "query_id": qid,
                "query_type": q["query_type"],
                "score": s,
            }, ensure_ascii=False) + "\n")
            out.flush()
            print(f"  {qid} [{q['query_type']}] -> {s}")
            time.sleep(0.3)


if __name__ == "__main__":
    main()