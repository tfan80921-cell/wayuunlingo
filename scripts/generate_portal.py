#!/usr/bin/env python3
"""
generate_portal.py — Regenera el portal HTML de Wayuunlingo a partir de los datos del repo.

Uso:
    python scripts/generate_portal.py
    python scripts/generate_portal.py --kpis-only

Lee:
    - data/evaluation_history.json
    - data/corpus_sample.json (opcional)

Escribe:
    - kpi_dashboard.html (siempre actualizado desde el JSON)
    - docs/project_portal.html (plantilla viva)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
HISTORY_FILE = DATA_DIR / "evaluation_history.json"
CORPUS_FILE = DATA_DIR / "corpus_sample.json"
PORTAL_OUT = DOCS_DIR / "project_portal.html"
KPI_OUT = ROOT / "kpi_dashboard.html"

PROJECT_VERSION = "v1.2-Qwen2.5-LoRA"
PROJECT_STATUS = "Activo"
CORPUS_STATUS = "en construcción (otro equipo)"


def load_history():
    if not HISTORY_FILE.exists():
        print(f"[WARN] No se encontró {HISTORY_FILE}")
        return []
    with open(HISTORY_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_corpus_count():
    if not CORPUS_FILE.exists():
        return 0
    with open(CORPUS_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return len(data)


def latest_metrics(history):
    if not history:
        return {
            "chrF++": "—",
            "BLEU": "—",
            "adequacy_eib": "—",
            "test_pairs": "—",
            "model_version": PROJECT_VERSION,
        }
    sorted_h = sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
    latest = sorted_h[0]
    return {
        "chrF++": latest.get("chrF++", "—"),
        "BLEU": latest.get("BLEU", "—"),
        "adequacy_eib": latest.get("adequacy_eib", "—"),
        "test_pairs": latest.get("test_pairs", "—"),
        "model_version": latest.get("model_version", PROJECT_VERSION),
        "cosine_similarity": latest.get("cosine_similarity", "—"),
        "fluency_eib": latest.get("fluency_eib", "—"),
        "result": latest.get("result", "—"),
    }


def result_class(result: str) -> str:
    r = (result or "").lower()
    if "aprobado" in r:
        return "ok"
    if "ajuste" in r or "requiere" in r:
        return "warn"
    return ""


def build_history_rows(history):
    rows = []
    sorted_h = sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)
    for i, item in enumerate(sorted_h):
        ts = item.get("timestamp", "")[:10]
        ver = item.get("model_version", "—")
        pairs = item.get("test_pairs", "—")
        chrf = item.get("chrF++", "—")
        bleu = item.get("BLEU", "—")
        cos = item.get("cosine_similarity", "—")
        adeq = item.get("adequacy_eib", "—")
        res = item.get("result", "—")
        cls = result_class(str(res))
        strong = "<strong>" if i == 0 else ""
        strong_end = "</strong>" if i == 0 else ""
        rows.append(
            f"""          <tr>
            <td>{ts}</td>
            <td>{strong}{ver}{strong_end}</td>
            <td>{pairs}</td>
            <td>{strong}{chrf}{strong_end}</td>
            <td>{bleu}</td>
            <td>{cos}</td>
            <td>{adeq}/5</td>
            <td class=\"{cls}\">{res}</td>
          </tr>"""
        )
    return "\n".join(rows)


def generate_kpi_dashboard(history, metrics):
    rows = build_history_rows(history)
    chrf = metrics.get("chrF++", "—")
    bleu = metrics.get("BLEU", "—")
    adeq = metrics.get("adequacy_eib", "—")
    pairs = metrics.get("test_pairs", "—")
    version = metrics.get("model_version", PROJECT_VERSION)

    return f"""<!DOCTYPE html>
<html lang=\"es\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Wayuunlingo — Dashboard de KPIs</title>
  <style>
    :root {{
      --bg: #0f172a; --card: #1e293b; --accent: #f59e0b; --accent2: #10b981;
      --text: #f1f5f9; --muted: #94a3b8; --border: #334155;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, sans-serif;
      background: var(--bg); color: var(--text); line-height: 1.5;
      padding: 2rem 1rem;
    }}
    .container {{ max-width: 1100px; margin: 0 auto; }}
    header {{ text-align: center; margin-bottom: 2.5rem; }}
    header h1 {{ font-size: 2rem; font-weight: 700; }}
    header p {{ color: var(--muted); margin-top: 0.5rem; }}
    .badge {{
      display: inline-block; background: var(--accent2); color: #064e3b;
      font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.75rem;
      border-radius: 999px; margin-top: 0.75rem;
    }}
    .kpis {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1.25rem; margin-bottom: 2.5rem;
    }}
    .kpi-card {{
      background: var(--card); border: 1px solid var(--border);
      border-radius: 12px; padding: 1.5rem; text-align: center;
    }}
    .kpi-card .label {{ font-size: 0.85rem; color: var(--muted); margin-bottom: 0.5rem; }}
    .kpi-card .value {{ font-size: 2.25rem; font-weight: 700; color: var(--accent); }}
    .kpi-card .meta {{ font-size: 0.8rem; color: var(--accent2); margin-top: 0.4rem; }}
    .section-title {{
      font-size: 1.25rem; font-weight: 600; margin-bottom: 1rem;
      border-left: 4px solid var(--accent); padding-left: 0.75rem;
    }}
    table {{
      width: 100%; border-collapse: collapse; background: var(--card);
      border-radius: 12px; overflow: hidden; border: 1px solid var(--border);
    }}
    th, td {{ padding: 0.85rem 1rem; text-align: left; border-bottom: 1px solid var(--border); font-size: 0.9rem; }}
    th {{ background: #0f172a; color: var(--muted); font-weight: 600; text-transform: uppercase; font-size: 0.75rem; }}
    tr:last-child td {{ border-bottom: none; }}
    .ok {{ color: var(--accent2); font-weight: 600; }}
    .warn {{ color: #fbbf24; font-weight: 600; }}
    footer {{ text-align: center; margin-top: 3rem; color: var(--muted); font-size: 0.85rem; }}
  </style>
</head>
<body>
  <div class=\"container\">
    <header>
      <h1>Wayuunlingo — Dashboard de KPIs</h1>
      <p>Seguimiento de Desempeño del Modelo de Traducción Español ↔ Wayuunaiki</p>
      <span class=\"badge\">Estado: {version} ({PROJECT_STATUS})</span>
    </header>

    <div class=\"kpis\">
      <div class=\"kpi-card\">
        <div class=\"label\">chrF++ (Morfemas / Subpalabras)</div>
        <div class=\"value\">{chrf}</div>
        <div class=\"meta\">Meta: ≥ 45.0</div>
      </div>
      <div class=\"kpi-card\">
        <div class=\"label\">BLEU Subpalabras</div>
        <div class=\"value\">{bleu}</div>
        <div class=\"meta\">Meta: ≥ 20.0</div>
      </div>
      <div class=\"kpi-card\">
        <div class=\"label\">Adecuación Semántica (EIB)</div>
        <div class=\"value\">{adeq} / 5.0</div>
        <div class=\"meta\">Meta: ≥ 4.0</div>
      </div>
      <div class=\"kpi-card\">
        <div class=\"label\">Pares en Corpus de Test</div>
        <div class=\"value\">{pairs}</div>
        <div class=\"meta\">Actualizado automáticamente</div>
      </div>
    </div>

    <h2 class=\"section-title\">Registro Histórico de Evaluaciones</h2>
    <table>
      <thead>
        <tr>
          <th>Fecha</th><th>Versión</th><th>Pares Test</th><th>chrF++</th>
          <th>BLEU</th><th>Cosine</th><th>Adecuación</th><th>Resultado</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>

    <footer>
      <p>Wayuunlingo · Generado el {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")} UTC · scripts/generate_portal.py</p>
    </footer>
  </div>
</body>
</html>
"""


def main():
    print("=== Wayuunlingo Portal Generator ===")
    history = load_history()
    metrics = latest_metrics(history)
    corpus_count = load_corpus_count()

    print(f"  Histórico: {len(history)} entradas")
    print(f"  Última versión: {metrics.get('model_version')}")
    print(f"  chrF++: {metrics.get('chrF++')} | BLEU: {metrics.get('BLEU')}")
    print(f"  Corpus sample: {corpus_count} pares")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    kpi_html = generate_kpi_dashboard(history, metrics)
    KPI_OUT.write_text(kpi_html, encoding="utf-8")
    print(f"  ✓ Escrito: {KPI_OUT.relative_to(ROOT)}")

    if not PORTAL_OUT.exists():
        print(f"  [INFO] {PORTAL_OUT} no existe aún.")
    else:
        print(f"  ✓ Portal existente: {PORTAL_OUT.relative_to(ROOT)}")

    print("Listo.")


if __name__ == "__main__":
    main()
