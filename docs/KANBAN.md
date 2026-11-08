# Wayuunlingo — Kanban

**Actualizado:** 2026-11-08  
**Ramas:** solo `main`.

## Ciclo cerrado (prioridad)

Doc: [CLOSED_LOOP.md](./CLOSED_LOOP.md) · SQL: `sql/closed_loop_schema.sql` · Script: `scripts/log_run_to_neon.py`

| ID | Tarjeta | Estado |
|----|---------|--------|
| C1 | Schema Neon ciclo cerrado aplicado | To do (correr SQL en tu Neon) |
| C2 | Primer run Kaggle/Colab → `experiment_runs` | To do |
| C3 | Eval solo golden v0.2 + `gate_passed` + QUALITY_LOG | To do |
| C4 | Floor chrF en `app_metadata` / primer baseline | To do |
| C5 | `prod_artifacts` current (cuando haya artefacto) | To do |
| C6 | Validación nativa golden (1–2 hablantes) | To do |

## Hechos verificados (pipeline datos)

| Tarea | Estado | Evidencia |
|-------|--------|-----------|
| T1 Dict CSV | Hecho (local) | data/external/dict/… |
| T2 AmericasNLP | Hecho (local) | sparse clone |
| T3 processed+domain | Hecho (local) | scripts/build_processed_splits.py |
| T4 baseline dict v0 | Hecho (local) | scripts/baseline_dict_rag.py |
| T5 por dominio | Hecho (local) | evaluation_history |
| Golden v0.2 | Hecho | data/golden_set/ · GOLDEN_SET_PROCESS.md |

## To Do de modelado

| ID | Tarjeta | P |
|----|---------|---|
| T4b | Baseline dict+LLM en prompt | P0 |
| T6 | LoRA post-baseline | P1 |
| T7 | Test bible + EIB | P1 |
| T9 | API translate (solo artefacto current) | P1 |

## Hallazgo

Lookup solo-CSV sobre dev ≈ chrF muy bajo. Gate y claims de producto van por **golden**, no por dev ruidoso.
