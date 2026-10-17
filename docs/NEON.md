# Wayuunlingo — Neon + pgvector (Estándar de datos)

**Estado:** Documentación de diseño (alineada a pdf-voice-ai y cotorr)  
**Fecha:** 2026-10-17  
**Regla general del ecosistema:** todos los proyectos usan **NeonDB** con extensión **pgvector**.

---

## 1. Propósito

Definir cómo Wayuunlingo persiste:

- Pares de traducción y metadatos del corpus  
- Runs de fine-tuning y métricas  
- Embeddings para búsqueda / validación / RAG futuro  
- (Cuando exista app) datos de usuario ligados a Auth  

El **source of truth del histórico de evaluación en la fase actual de pipeline** sigue siendo `data/evaluation_history.json`. Neon es el siguiente escalón cuando haya API multi-usuario o necesidad de consulta vectorial.

---

## 2. Convención de entorno

```bash
# .env (nunca en git)
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require
```

- Región recomendada: la misma que uses en el resto de proyectos (p. ej. `aws-us-east-2` / Ohio, como en pdf-voice-ai).  
- Crear proyecto Neon dedicado o branch por entorno (`dev` / `prod`).  
- Documentar el `project-id` internamente; no commitear secretos.

Referencia operativa: repo `pdf-voice-ai` → `NEON.md` (CLI `neon`, `neon link`, `neon env pull`).

---

## 3. Extensión y dimensiones

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

| Uso | Dimensión sugerida | Notas |
|-----|---------------------|--------|
| Embeddings de pares / chunks de corpus | **384** o **768** | 384 ≈ MiniLM (pdf-voice-ai); 768 ≈ cotorr. **Fijar una** al elegir el modelo y no mezclar. |
| Índice | IVFFlat o HNSW | IVFFlat con `lists` acotado al inicio; HNSW si el volumen crece |

Si cambia el modelo de embeddings, hay que migrar la columna `vector(N)` y reindexar.

---

## 4. Schema previsto

### 4.1 Corpus y pares

```sql
CREATE TABLE IF NOT EXISTS translation_pairs (
    id            TEXT PRIMARY KEY,
    spanish       TEXT NOT NULL,
    wayuunaiki    TEXT NOT NULL,
    source        TEXT NOT NULL DEFAULT '',
    domain        TEXT NOT NULL DEFAULT '',
    split         TEXT NOT NULL DEFAULT 'train',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pairs_split ON translation_pairs (split);
CREATE INDEX IF NOT EXISTS idx_pairs_domain ON translation_pairs (domain);
```

### 4.2 Embeddings de pares

```sql
CREATE TABLE IF NOT EXISTS pair_embeddings (
    pair_id       TEXT PRIMARY KEY REFERENCES translation_pairs(id) ON DELETE CASCADE,
    embedding     vector(384),
    model_name    TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_pair_embedding
    ON pair_embeddings
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
```

### 4.3 Runs de entrenamiento / evaluación

```sql
CREATE TABLE IF NOT EXISTS training_runs (
    run_id          TEXT PRIMARY KEY,
    model_base      TEXT NOT NULL,
    model_version   TEXT NOT NULL,
    config_hash     TEXT NOT NULL DEFAULT '',
    test_pairs      INT,
    chrf_plus       REAL,
    bleu            REAL,
    cosine_sim      REAL,
    adequacy_eib    REAL,
    fluency_eib     REAL,
    gates_passed    BOOLEAN,
    result          TEXT NOT NULL DEFAULT '',
    artifact_path   TEXT NOT NULL DEFAULT '',
    notes           TEXT NOT NULL DEFAULT '',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### 4.4 Muestras de evaluación (opcional)

```sql
CREATE TABLE IF NOT EXISTS evaluation_samples (
    id              BIGSERIAL PRIMARY KEY,
    run_id          TEXT NOT NULL REFERENCES training_runs(run_id) ON DELETE CASCADE,
    source_text     TEXT NOT NULL,
    reference_text  TEXT NOT NULL,
    hypothesis_text TEXT NOT NULL,
    chrf_local      REAL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_eval_samples_run ON evaluation_samples (run_id);
```

### 4.5 Metadata de app

```sql
CREATE TABLE IF NOT EXISTS app_metadata (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
```

---

## 5. Bootstrap en aplicación

Patrón (como `app/db.py` en pdf-voice-ai):

1. Sin `DATABASE_URL` → solo archivos locales / pipeline offline.  
2. Con URL → extension `vector` + tablas IF NOT EXISTS.  
3. Registrar codec pgvector.  
4. Índices vectoriales con manejo de error si hay pocas filas.

| Capa | Opción A (Python) | Opción B (TS) |
|------|-------------------|---------------|
| Stack | SQLAlchemy async + asyncpg | Drizzle + pg Pool |

Pipeline de fine-tuning: puede seguir con JSON; sync a `training_runs` es paso posterior.

---

## 6. Flujo de datos recomendado

```
Pipeline → evaluation_report.json → evaluation_history.json → (opcional) UPSERT training_runs
Corpus estable → translation_pairs (+ pair_embeddings)
```

---

## 7. Seguridad

- `DATABASE_URL` solo en secretos.  
- No SQL crudo desde el cliente.  
- Branches Neon para experimentos.  
- Export periódico del golden set.

---

## 8. Criterios de aceptación

- [ ] Documento y schema acordados.  
- [ ] Dimensión de embeddings fijada antes del load masivo.  
- [ ] Pipeline funciona sin Neon.  
- [ ] Health check con extensión `vector` al activar API.

---

## 9. Referencias

- `pdf-voice-ai`: NEON.md, app/db.py, sql/schema.sql  
- `cotorr`: Drizzle + pgvector 768  
- Wayuunlingo: docs/FINE_TUNING_PIPELINE.md
