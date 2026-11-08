#!/usr/bin/env python3
"""
Registra un run del ciclo cerrado en Neon.

Uso (local / Colab / Kaggle al final del notebook):

  export DATABASE_URL='postgresql://...'
  python scripts/log_run_to_neon.py --run-id exp001 --chrf 12.5 --gate-passed \\
      --golden-version v0.2 --model-base dict-rag --source kaggle

Sin DATABASE_URL: imprime el payload JSON y sale 0 (útil en CI sin secretos).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Log experiment run to Neon")
    p.add_argument("--run-id", required=True)
    p.add_argument("--project", default="wayuunlingo")
    p.add_argument("--source", default="local", choices=["kaggle", "colab", "local", "ci"])
    p.add_argument("--model-base", default="")
    p.add_argument("--model-version", default="")
    p.add_argument("--config-hash", default="")
    p.add_argument("--data-hash", default="")
    p.add_argument("--golden-version", default="v0.2")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--notebook-ref", default="")
    p.add_argument("--chrf", type=float, default=None)
    p.add_argument("--bleu", type=float, default=None)
    p.add_argument("--gate-passed", action="store_true")
    p.add_argument("--status", default="completed")
    p.add_argument("--artifact-uri", default="")
    p.add_argument("--notes", default="")
    p.add_argument(
        "--metric",
        action="append",
        default=[],
        help="Extra metric name=value or name=value=domain (repeatable)",
    )
    return p.parse_args()


def parse_metrics(raw: list[str]) -> list[tuple[str, float, str]]:
    out: list[tuple[str, float, str]] = []
    for item in raw:
        parts = item.split("=")
        if len(parts) == 2:
            out.append((parts[0], float(parts[1]), ""))
        elif len(parts) == 3:
            out.append((parts[0], float(parts[1]), parts[2]))
        else:
            raise SystemExit(f"Métrica inválida: {item}")
    return out


def main() -> int:
    args = parse_args()
    metrics = parse_metrics(args.metric)

    payload = {
        "run_id": args.run_id,
        "project": args.project,
        "source": args.source,
        "model_base": args.model_base,
        "model_version": args.model_version,
        "config_hash": args.config_hash
        or hashlib.sha256(args.model_base.encode()).hexdigest()[:12],
        "data_hash": args.data_hash,
        "golden_version": args.golden_version,
        "seed": args.seed,
        "notebook_ref": args.notebook_ref,
        "chrf_plus": args.chrf,
        "bleu": args.bleu,
        "gate_passed": bool(args.gate_passed),
        "status": args.status,
        "artifact_uri": args.artifact_uri,
        "notes": args.notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "metrics": [
            {"metric_name": n, "metric_value": v, "domain": d} for n, v, d in metrics
        ],
    }

    database_url = os.environ.get("DATABASE_URL") or os.environ.get("NEON_DATABASE_URL")
    if not database_url:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print("\n# Sin DATABASE_URL — solo dry-run. No se escribió en Neon.", file=sys.stderr)
        return 0

    try:
        import psycopg2
    except ImportError:
        print("Instala psycopg2-binary: pip install psycopg2-binary", file=sys.stderr)
        return 1

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO experiment_runs (
                    run_id, project, source, model_base, model_version,
                    config_hash, data_hash, golden_version, seed, notebook_ref,
                    chrf_plus, bleu, gate_passed, status, artifact_uri, notes
                ) VALUES (
                    %(run_id)s, %(project)s, %(source)s, %(model_base)s, %(model_version)s,
                    %(config_hash)s, %(data_hash)s, %(golden_version)s, %(seed)s, %(notebook_ref)s,
                    %(chrf_plus)s, %(bleu)s, %(gate_passed)s, %(status)s, %(artifact_uri)s, %(notes)s
                )
                ON CONFLICT (run_id) DO UPDATE SET
                    chrf_plus = EXCLUDED.chrf_plus,
                    bleu = EXCLUDED.bleu,
                    gate_passed = EXCLUDED.gate_passed,
                    status = EXCLUDED.status,
                    artifact_uri = EXCLUDED.artifact_uri,
                    notes = EXCLUDED.notes
                """,
                payload,
            )
            for n, v, d in metrics:
                cur.execute(
                    """
                    INSERT INTO run_metrics (run_id, metric_name, metric_value, domain)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (run_id, metric_name, domain)
                    DO UPDATE SET metric_value = EXCLUDED.metric_value
                    """,
                    (args.run_id, n, v, d),
                )
        conn.commit()
    finally:
        conn.close()

    print(f"OK run_id={args.run_id} gate_passed={args.gate_passed} chrf={args.chrf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
