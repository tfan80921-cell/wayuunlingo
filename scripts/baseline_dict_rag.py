#!/usr/bin/env python3
"""Baseline dict-lookup ES→guc (sin GPU). Ver docs/KANBAN.md T4."""
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import sacrebleu

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DICT = ROOT / "data/external/dict/wayuunaiki_dictionary.csv"
DEFAULT_TEST = ROOT / "data/processed/test.jsonl"
HISTORY = ROOT / "data/evaluation_history.json"


def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return " ".join(text.strip().split())


def load_dict(path: Path) -> list[tuple[str, str]]:
    pairs = []
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            es = clean(row.get("spanish") or row.get("es") or "")
            guc = clean(row.get("wayuunaiki") or row.get("guc") or "")
            if es and guc:
                pairs.append((es.lower(), guc))
    pairs.sort(key=lambda x: len(x[0]), reverse=True)
    return pairs


def tokenize_es(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", text.lower(), flags=re.UNICODE)


def translate_dict_rag(source: str, glossary: list[tuple[str, str]], max_hits: int = 40) -> str:
    s = clean(source)
    remaining = s.lower()
    hits = 0
    for es, guc in glossary:
        if hits >= max_hits:
            break
        if " " in es and es in remaining:
            remaining = remaining.replace(es, f" {guc} ", 1)
            hits += 1
    tokens = tokenize_es(remaining)
    word_map = {es: guc for es, guc in glossary if " " not in es}
    out_tokens = []
    for tok in tokens:
        if tok in word_map:
            out_tokens.append(word_map[tok])
        elif tok.isalpha():
            continue
        else:
            out_tokens.append(tok)
    return re.sub(r"\s+", " ", " ".join(out_tokens)).strip()


def read_jsonl(path: Path, limit):
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows


def metrics(preds, refs):
    bleu = sacrebleu.corpus_bleu(preds, [refs])
    chrf = sacrebleu.corpus_chrf(preds, [refs], word_order=2)
    return {"chrF++": round(chrf.score, 2), "BLEU": round(bleu.score, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dict", type=Path, default=DEFAULT_DICT)
    ap.add_argument("--test", type=Path, default=DEFAULT_TEST)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--preds-out", type=Path, default=ROOT / "outputs/baseline_dict_rag_preds.jsonl")
    ap.add_argument("--no-history", action="store_true")
    args = ap.parse_args()
    if not args.dict.exists():
        raise SystemExit(f"Falta diccionario: {args.dict}")
    if not args.test.exists():
        raise SystemExit(f"Falta test: {args.test}")
    glossary = load_dict(args.dict)
    rows = read_jsonl(args.test, args.limit)
    print(f"Dict entries: {len(glossary)} | Test rows: {len(rows)}")
    preds_rows = []
    by_domain = defaultdict(list)
    for r in rows:
        hyp = translate_dict_rag(r["source"], glossary)
        domain = r.get("domain") or "unknown"
        preds_rows.append({"id": r.get("id"), "source": r["source"], "target": r["target"], "prediction": hyp, "domain": domain})
        by_domain[domain].append((hyp, r["target"]))
    args.preds_out.parent.mkdir(parents=True, exist_ok=True)
    with args.preds_out.open("w", encoding="utf-8") as f:
        for row in preds_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    overall = metrics([r["prediction"] for r in preds_rows], [r["target"] for r in preds_rows])
    print("=== Baseline dict-lookup ===")
    print(json.dumps({"overall": overall, "n": len(rows)}, indent=2))
    domain_report = {}
    for dom, pairs in sorted(by_domain.items(), key=lambda x: -len(x[1])):
        m = metrics([a for a, _ in pairs], [b for _, b in pairs])
        domain_report[dom] = {"n": len(pairs), **m}
        print(f"  {dom}: n={len(pairs)} chrF++={m['chrF++']} BLEU={m['BLEU']}")
    report = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model_version": "baseline-dict-lookup-v0",
        "test_pairs": len(rows),
        "chrF++": overall["chrF++"],
        "BLEU": overall["BLEU"],
        "by_domain": domain_report,
        "result": "Baseline léxico (sin LoRA)",
    }
    (ROOT / "outputs/baseline_dict_rag_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if not args.no_history:
        history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
        history.append({
            "timestamp": report["timestamp"],
            "model_version": report["model_version"],
            "test_pairs": report["test_pairs"],
            "chrF++": report["chrF++"],
            "BLEU": report["BLEU"],
            "cosine_similarity": None,
            "adequacy_eib": None,
            "fluency_eib": None,
            "result": report["result"],
            "by_domain": domain_report,
        })
        HISTORY.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Updated", HISTORY)


if __name__ == "__main__":
    main()
