# Ciclo cerrado — de experimento a producto confiable

**Estado:** operativo · 2026-11-08  
**Objetivo:** dato confiable → eval honesta → artefacto único → uso → feedback → otra vez.

Este documento **cierra el ciclo** del ecosistema Wayuunlingo (y se alinea con Kaggle/Colab + Neon + LiteLLM). No reemplaza `GOLDEN_SET_PROCESS.md` ni `KPI_FRAMEWORK.md`; los conecta.

---

## 1. Diagrama del ciclo

```text
┌──────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Corpus +     │────►│ Pipeline     │────►│ Neon: runs +    │
│ Golden set   │     │ Kaggle/Colab │     │ metrics + gate  │
└──────▲───────┘     └──────────────┘     └────────┬────────┘
       │                                           │
       │              gate PASS                    ▼
       │                                   ┌───────────────┐
       │                                   │ Artefacto     │
       │                                   │ PROD current  │
       │                                   └───────┬───────┘
       │                                           │
       │         feedback / correcciones           ▼
       └──────────────────────────────────  App / hablantes
```

**Regla de oro:** nada se llama “producción” si no pasó el **gate del golden set** y quedó registrado en Neon (o, mientras tanto, en `QUALITY_LOG.md` + `evaluation_history.json`).

---

## 2. Los cinco cierres

| # | Cierre | Qué hacer | Evidencia |
|---|--------|-----------|-----------|
| 1 | **Eval que no miente** | Solo golden (y dominios etiquetados); chrF++ por dominio | `experiment_runs` + `run_metrics` |
| 2 | **Gate de regresión** | Si chrF++ (o score acordado) &lt; baseline del golden → `gate_passed=false` | columna `gate_passed` |
| 3 | **Un artefacto prod** | Un solo puntero `prod_current` → run_id + path del modelo | tabla `prod_artifacts` |
| 4 | **Feedback humano** | Correcciones / thumbs → filas reutilizables | `feedback_events` |
| 5 | **Historia reproducible** | Cada run: config_hash, data_hash, notebook/kernel, seed | `experiment_runs` |

---

## 3. Golden set (fuente de verdad de calidad)

| Item | Ruta / nota |
|------|-------------|
| Set actual | `data/golden_set/golden_set_v0.2.json` (22 pares) |
| Proceso | [GOLDEN_SET_PROCESS.md](./GOLDEN_SET_PROCESS.md) |
| Log humano | [QUALITY_LOG.md](./QUALITY_LOG.md) |
| Validación nativa | **Pendiente** — prioritaria antes de claims públicos |

**Política de gate (v1):**

1. Evaluar **siempre** sobre el golden versionado (`golden_version` en el run).  
2. Baseline mínima inicial: la del mejor run ya registrado con ese `golden_version` (o un floor manual en `app_metadata`, ej. `chrf_floor_golden=5.0` hasta tener señal).  
3. `gate_passed = (chrf_plus >= floor)` y sin error de pipeline.  
4. Métricas viejas sin golden documentado **no** promocionan a prod.

Cuando haya validación nativa, subir floor y registrar en `QUALITY_LOG.md`.

---

## 4. Schema Neon (aplicar una vez)

Archivo SQL: [`sql/closed_loop_schema.sql`](../sql/closed_loop_schema.sql)

Tablas:

- `experiment_runs` — un row por job Kaggle/Colab/local  
- `run_metrics` — métricas largas (chrF por dominio, etc.)  
- `prod_artifacts` — puntero de producción  
- `feedback_events` — señales de hablantes/usuarios  
- `data_cards` — licencia/procedencia de datasets  

Compatibilidad: convive con `training_runs` de [NEON.md](./NEON.md). Preferir **`experiment_runs`** para el ciclo nuevo; migrar lecturas cuando puedas.

```bash
# Desde máquina con psql y DATABASE_URL
psql "$DATABASE_URL" -f sql/closed_loop_schema.sql
```

---

## 5. Pipeline Kaggle / Colab → Neon

Al **final** de cada notebook (éxito o fracaso controlado):

1. Calcular métricas solo sobre golden (y opcionalmente dev por dominio).  
2. Escribir JSON local de respaldo (`data/runs/<run_id>.json`).  
3. Si hay `DATABASE_URL`, insertar run + metrics (script [`scripts/log_run_to_neon.py`](../scripts/log_run_to_neon.py)).  
4. Si `gate_passed`, opcionalmente proponer promoción (no automática sin revisión humana al inicio).

Secretos en Kaggle/Colab: **Add-ons → secrets** (`DATABASE_URL`), nunca en celdas commiteadas.

Campos mínimos del run:

```text
run_id, project, source (kaggle|colab|local),
model_base, config_hash, data_hash, golden_version,
chrf_plus, gate_passed, artifact_uri, notes, created_at
```

---

## 6. Ruta única a producción

| Rol | Qué es |
|-----|--------|
| Experimentos | Cualquier run en Neon con `gate_passed` true/false |
| **PROD current** | Una sola fila activa en `prod_artifacts` (`is_current=true`) |

Promoción (manual v1):

```sql
UPDATE prod_artifacts SET is_current = false WHERE project = 'wayuunlingo';
INSERT INTO prod_artifacts (project, run_id, artifact_uri, is_current, promoted_by, notes)
VALUES ('wayuunlingo', '<run_id>', '<s3|kaggle|path>', true, '<quien>', 'pasó golden v0.2');
```

La API / demo solo carga el artefacto `is_current=true`. Nada de “el notebook de la semana pasada”.

---

## 7. Feedback → datos

Cuando un hablante o usuario corrija una traducción:

1. Insertar en `feedback_events` (`source_text`, `model_output`, `correction`, `rating`, `reviewer`).  
2. Revisión periódica (semanal): correcciones validadas → candidatos a golden o a train (con `data_cards`).  
3. Nunca mezclar feedback crudo al golden sin paso humano.

UI mínima (futuro): pulgar arriba/abajo + caja de corrección en la app de traducción.

---

## 8. LiteLLM / cascada (lado serving)

Para el producto que sirva modelos vía [llm-gateway](https://github.com/tfan80921-cell/llm-gateway):

- Loguear en el producto o en LiteLLM **qué deployment** respondió (groq / gemini / openrouter).  
- Si la cascada se agota → evento de error + no contar como `resolved` en KPIs.  
- Contrato de KPIs: [KPI_FRAMEWORK.md](./KPI_FRAMEWORK.md).

---

## 9. Checklist “ciclo cerrado” (esta semana)

- [ ] Aplicar `sql/closed_loop_schema.sql` en el Neon del proyecto  
- [ ] Un run real desde Kaggle/Colab que inserte en `experiment_runs`  
- [ ] Evaluar **solo** golden v0.2 y registrar `gate_passed`  
- [ ] Entrada en `QUALITY_LOG.md` con el resultado  
- [ ] Definir floor chrF inicial en `app_metadata` o primer baseline  
- [ ] (Si hay modelo desplegable) una fila `prod_artifacts` current  
- [ ] Agenda de validación nativa del golden (1–2 personas)  

---

## 10. Referencias

| Doc | Rol |
|-----|-----|
| [GOLDEN_SET_PROCESS.md](./GOLDEN_SET_PROCESS.md) | Cómo nació el golden |
| [QUALITY_LOG.md](./QUALITY_LOG.md) | Log humano |
| [NEON.md](./NEON.md) | Estándar vector + schema previo |
| [FINE_TUNING_PIPELINE.md](./FINE_TUNING_PIPELINE.md) | Slot de train |
| [KPI_FRAMEWORK.md](./KPI_FRAMEWORK.md) | Costo / negocio en serving |
