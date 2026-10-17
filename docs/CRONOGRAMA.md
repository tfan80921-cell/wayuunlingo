# Wayuunlingo — Cronograma (incorporación de oro público + pipeline)

**Versión:** 1.1 · 2026-10-17  
**Horizonte:** ~8 semanas desde la consolidación de docs (ajustable al ritmo del corpus EIB)

Fuentes: AmericasNLP 2025, wayuunaiki-qlora-lab (dict + lecciones), norgrai/wayuunaiki, stack propio (cotorr, Neon, Auth).

---

## Vista por semanas

| Semana | Foco | Entregables |
|--------|------|-------------|
| **S0** (hecho) | Diseño y estándares | Pipeline, NEON, AUTH, AUDIO, LEGACY, configs baseline/lora, data/external/README |
| **S1** | Datos públicos en disco | Dict CSV; AmericasNLP o HF; JSONL con `domain` |
| **S2** | Baseline medible | Zero-shot + **dict-RAG**; chrF++/BLEU global y por dominio; evaluation_history |
| **S3** | Process formal | process_data + NFKC/dedup; configs → data/processed/ |
| **S4** | Primer LoRA controlado | Run corto tras baseline; mismo test; Δ chrF++ |
| **S5** | Morph opcional | Morfessor/PRPE subset (Norgrai) |
| **S6** | Golden / EIB | Pares propios + scoring humano |
| **S7** | Producto mínimo | /api/translate + STT/TTS cotorr (ES) |
| **S8** | Cierre de ciclo | Neon training_runs opcional; portal; kanban al día |

---

## Hitos

| ID | Hito | Criterio de hecho |
|----|------|-------------------|
| M1 | Datos externos listos | dict CSV + processed train/val/test |
| M2 | Baseline dict-RAG numerado | chrF++/BLEU en histórico (+ por dominio) |
| M3 | LoRA ≥ baseline | Δ chrF++ documentado mismo test |
| M4 | Test no solo-diccionario | bible/natural o EIB reportado |
| M5 | Voz ES → MT → TTS | Demo end-to-end |

---

## Oro público — cuándo y cómo

**AmericasNLP 2025:** S1–S3; JSONL con domain; métricas por dominio (89% dict).

**qlora-lab:** S1 dict; S2 baseline RAG; S4 comparar LoRA; no producción sin EIB.

**norgrai:** S5 morph; bitext secundario con origen anotado.

---

## Riesgos

| Riesgo | Mitigación |
|--------|------------|
| EIB se retrasa | S1–S4 solo con público |
| Métricas infladas por dict | Report por dominio obligatorio S2+ |
| Sin GPU | Baseline dict-RAG igual avanza |
| Scope Duolingo | Backlog kanban, no S1–S4 |

Estado día a día: `docs/KANBAN.md`.
