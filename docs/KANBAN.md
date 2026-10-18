# Wayuunlingo — Kanban

**Actualizado:** 2026-10-18  
**Ramas:** solo `main`. No rehacer T1–T3 si los artefactos ya están en disco.

## Hechos verificados (2026-10-18)

| Tarea | Estado | Evidencia |
|-------|--------|-----------|
| T1 Dict CSV | Hecho (local) | data/external/dict/wayuunaiki_dictionary.csv (~2000) |
| T2 AmericasNLP | Hecho (local) | sparse clone wayuu-spanish 59.7k/6.6k |
| T3 processed+domain | Hecho (local) | scripts/build_processed_splits.py |
| T4 baseline dict v0 | Hecho (local) | scripts/baseline_dict_rag.py; lookup sin LLM |
| T5 por dominio | Hecho (local) | by_domain en evaluation_history |

## To Do de valor

| ID | Tarjeta | P |
|----|---------|---|
| T4b | Baseline dict+LLM en prompt (qlora-lab) | P0 |
| T6 | LoRA post-baseline LLM | P1 |
| T7 | Test bible + EIB | P1 |
| T9 | API translate | P1 |
| T8/T10/T11 | Morph / voz / Neon | P2 |

## Hallazgo

Lookup solo-CSV sobre dev ≈ chrF 0.6 (casi cero overlap CSV↔dev). No es el baseline dict-RAG+LLM. No re-clonar AmericasNLP si ya está en disco.
