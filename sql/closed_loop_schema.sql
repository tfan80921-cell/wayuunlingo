-- Wayuunlingo / ecosistema — ciclo cerrado (runs, gate, prod, feedback)
-- Aplicar: psql "$DATABASE_URL" -f sql/closed_loop_schema.sql
-- Compatible con docs/NEON.md (no borra training_runs existente)

CREATE EXTENSION IF NOT EXISTS vector;

-- ---------------------------------------------------------------------------
-- Runs de experimento (Kaggle / Colab / local)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS experiment_runs (
    run_id           TEXT PRIMARY KEY,
    project          TEXT NOT NULL DEFAULT 'wayuunlingo',
    source           TEXT NOT NULL DEFAULT 'local',  -- kaggle | colab | local | ci
    model_base       TEXT NOT NULL DEFAULT '',
    model_version    TEXT NOT NULL DEFAULT '',
    config_hash      TEXT NOT NULL DEFAULT '',
    data_hash        TEXT NOT NULL DEFAULT '',
    golden_version   TEXT NOT NULL DEFAULT '',
    seed             INT,
    notebook_ref     TEXT NOT NULL DEFAULT '',     -- URL kernel Kaggle / path
    chrf_plus        REAL,
    bleu             REAL,
    gate_passed      BOOLEAN NOT NULL DEFAULT false,
    status           TEXT NOT NULL DEFAULT 'completed',  -- completed | failed | running
    artifact_uri     TEXT NOT NULL DEFAULT '',
    notes            TEXT NOT NULL DEFAULT '',
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_experiment_runs_project_created
    ON experiment_runs (project, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_experiment_runs_gate
    ON experiment_runs (project, gate_passed);

-- Métricas adicionales (por dominio, etc.)
CREATE TABLE IF NOT EXISTS run_metrics (
    id          BIGSERIAL PRIMARY KEY,
    run_id      TEXT NOT NULL REFERENCES experiment_runs(run_id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,   -- chrf_plus | bleu | chrf_domain_dictionary | ...
    metric_value REAL NOT NULL,
    domain      TEXT NOT NULL DEFAULT '',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (run_id, metric_name, domain)
);

CREATE INDEX IF NOT EXISTS idx_run_metrics_run ON run_metrics (run_id);

-- ---------------------------------------------------------------------------
-- Artefacto de producción (un current por project)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS prod_artifacts (
    id            BIGSERIAL PRIMARY KEY,
    project       TEXT NOT NULL DEFAULT 'wayuunlingo',
    run_id        TEXT NOT NULL REFERENCES experiment_runs(run_id),
    artifact_uri  TEXT NOT NULL,
    is_current    BOOLEAN NOT NULL DEFAULT false,
    promoted_by   TEXT NOT NULL DEFAULT '',
    notes         TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_prod_one_current
    ON prod_artifacts (project)
    WHERE is_current = true;

-- ---------------------------------------------------------------------------
-- Feedback de hablantes / usuarios
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feedback_events (
    id              BIGSERIAL PRIMARY KEY,
    project         TEXT NOT NULL DEFAULT 'wayuunlingo',
    source_text     TEXT NOT NULL,
    model_output    TEXT NOT NULL DEFAULT '',
    correction      TEXT NOT NULL DEFAULT '',
    rating          SMALLINT,                 -- -1, 0, 1 o 1-5
    reviewer        TEXT NOT NULL DEFAULT '',
    lang_pair       TEXT NOT NULL DEFAULT 'es-guc',
    run_id          TEXT REFERENCES experiment_runs(run_id) ON DELETE SET NULL,
    promoted_to     TEXT NOT NULL DEFAULT '', -- '' | golden_candidate | train_candidate
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_feedback_project_created
    ON feedback_events (project, created_at DESC);

-- ---------------------------------------------------------------------------
-- Data cards (procedencia / licencia)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS data_cards (
    dataset_id    TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    source_url    TEXT NOT NULL DEFAULT '',
    license       TEXT NOT NULL DEFAULT '',
    domain        TEXT NOT NULL DEFAULT '',
    row_count     INT,
    notes         TEXT NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Metadata clave-valor (floors de gate, etc.)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS app_metadata (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT INTO app_metadata (key, value) VALUES
    ('chrf_floor_golden', '1.0'),
    ('golden_version_current', 'v0.2')
ON CONFLICT (key) DO NOTHING;
