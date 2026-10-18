#!/usr/bin/env python3
"""Construye data/processed/{train,val,test}.jsonl desde AmericasNLP wayuu-spanish con domain."""
from __future__ import annotations

import argparse
import json
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ANLP = ROOT / "data/external/americasnlp2025/ST1_MachineTranslation/data/wayuu-spanish"
OUT_DIR = ROOT / "data/processed"


def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return " ".join(text.strip().split())


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def build_split(es_path, guc_path, source_path, out_path, max_rows=None, id_prefix="es-guc"):
    es = read_lines(es_path)
    guc = read_lines(guc_path)
    domains = read_lines(source_path) if source_path and source_path.exists() else [""] * len(es)
    if not (len(es) == len(guc) == len(domains)):
        raise ValueError(f"Mismatch lines: es={len(es)} guc={len(guc)} domain={len(domains)}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    domain_counts: Counter = Counter()
    kept = 0
    with out_path.open("w", encoding="utf-8") as f:
        for i, (s, t, d) in enumerate(zip(es, guc, domains), start=1):
            if max_rows is not None and kept >= max_rows:
                break
            s, t = clean(s), clean(t)
            d = (d or "").strip() or "unknown"
            if not s or not t:
                continue
            key = (s, t)
            if key in seen:
                continue
            seen.add(key)
            row = {
                "id": f"{id_prefix}-{i}",
                "source_lang": "es",
                "target_lang": "guc",
                "source": s,
                "target": t,
                "domain": d,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            domain_counts[d] += 1
            kept += 1
    print(f"Wrote {kept} → {out_path}")
    for dom, n in domain_counts.most_common():
        print(f"  {dom}: {n}")
    return domain_counts


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--anlp-dir", type=Path, default=DEFAULT_ANLP)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    p.add_argument("--max-train", type=int, default=None)
    args = p.parse_args()
    base = args.anlp_dir
    if not base.exists():
        raise SystemExit(f"No existe {base}. Ver data/external/README.md")
    build_split(base / "train.es", base / "train.guc", base / "train.source", args.out_dir / "train.jsonl", args.max_train, "train")
    build_split(base / "dev.es", base / "dev.guc", base / "dev.source", args.out_dir / "val.jsonl", id_prefix="val")
    build_split(base / "dev.es", base / "dev.guc", base / "dev.source", args.out_dir / "test.jsonl", id_prefix="test")
    print("OK — splits en", args.out_dir)


if __name__ == "__main__":
    main()
