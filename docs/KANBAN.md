# Wayuunlingo — Kanban

**Actualizado:** 2026-10-17  
**Regla:** mover tarjetas al cerrar el criterio de hecho. Fechas: `CRONOGRAMA.md`.

---

## Backlog

| ID | Tarjeta | Notas |
|----|---------|--------|
| B1 | App tipo Duolingo | Tras motor MT estable |
| B2 | Diccionario producto (UI) | dict CSV + pgvector después |
| B3 | Chat conversacional wayuu | MT + STT/TTS |
| B4 | STT/TTS nativo guc | Requiere audio etiquetado |
| B5 | Repos legacy privados | Si aparecen, LEGACY_RESOURCES |

---

## Done

| ID | Tarjeta | Evidencia |
|----|---------|-----------|
| D1 | Diseño pipeline | FINE_TUNING_PIPELINE.md |
| D2 | Neon + Auth + Audio | NEON / AUTH / AUDIO_STT_TTS |
| D3 | Inventario oro público | LEGACY_RESOURCES.md |
| D4 | Datos externos documentados | data/external/README.md |
| D5 | Config baseline dict-RAG | configs/baseline_dict_rag.yaml |
| D6 | Config ejemplo LoRA | configs/example_lora.yaml |
| D7 | Dashboard scripts | generate_portal.py |
| D8 | Cronograma + kanban | CRONOGRAMA.md, KANBAN.md |

---

## To Do (orden)

| ID | Tarjeta | Criterio de hecho | P |
|----|---------|-------------------|---|
| T1 | Descargar dict CSV | `data/external/dict/...csv` | P0 |
| T2 | AmericasNLP guc o HF dataset | train/dev locales | P0 |
| T3 | processed train/val/test + domain | conteos por domain | P0 |
| T4 | Eval baseline dict-RAG | números + evaluation_history | P0 |
| T5 | Métricas por dominio | dictionary vs bible vs other | P0 |
| T6 | Primer LoRA post-baseline | Δ chrF++ mismo test | P1 |
| T7 | Test no-diccionario / EIB sample | número fuera de dict | P1 |
| T8 | Morph Morfessor subset | config flag + nota | P2 |
| T9 | API translate mínima | POST ES↔guc | P1 |
| T10 | STT/TTS cotorr (voz ES) | demo mic→MT→audio | P2 |
| T11 | Neon training_runs | upsert tras evaluate | P2 |

---

## Doing

| ID | Tarjeta | Owner | Notas |
|----|---------|-------|--------|
| — | *(empezar por T1)* | | |

---

## Estado de incorporación (oro público)

| Fuente | Estado |
|--------|--------|
| Dict qlora-lab | Docs + config; falta **T1 + T4** |
| AmericasNLP 2025 | Docs; falta **T2 + T3** |
| norgrai morph | Docs P2; falta **T8** |
| Lección dict-RAG > LoRA | Diseño; falta demostrar en histórico (**T4 vs T6**) |

Incorporado de verdad = documentado + config/script + número en evaluation_history.
