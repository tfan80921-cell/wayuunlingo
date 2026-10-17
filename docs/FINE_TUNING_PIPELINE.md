# Wayuunlingo — Pipeline de Fine-Tuning (Planeación v1.0)

**Estado:** Documento de diseño (sin implementación nueva de código)  
**Fecha:** 2026-10-17  
**Objetivo:** Definir un pipeline de fine-tuning **reproducible, configurado por archivo y automatizable**, alineado con el stack del proyecto (corpus ES↔Wayuunaiki, métricas chrF++, evaluación EIB) y con los estándares transversales (Neon + pgvector, Auth cuando exista app).

---

## 1. Propósito

Pasar de scripts sueltos (`process_data.py`, `train_model.py`, `evaluate.py`) a un **flujo único y controlado** que:

1. Tome un corpus paralelo ES–Wayuunaiki (train/val/test).
2. Opcionalmente aplique segmentación morfológica (crítico en lengua aglutinante).
3. Entrene un adaptador LoRA/QLoRA sobre un modelo base multilingüe.
4. Evalúe con **chrF++** (métrica principal), BLEU y señales semánticas.
5. Registre el run de forma trazable (JSON local → futuro Neon).
6. Actualice el dashboard de KPIs sin edición manual.

**Criterio de “pipeline listo”:** un solo comando (o un job en GPU) con config explícita produce checkpoint + informe + entrada en el histórico.

---

## 2. Alcance de esta versión

| Incluido | Fuera de alcance (por ahora) |
|----------|------------------------------|
| Diseño del flujo de extremo a extremo | Reescribir todo el código de entrenamiento |
| Esquema de configuración (YAML/JSON) | UI de lanzamiento de jobs |
| Contrato de entradas/salidas | Despliegue continuo del modelo en producción |
| Criterios de éxito y gates de calidad | Entrenamiento multi-nodo / distributed |
| Encaje con Neon y Auth (documental) | Implementación de tablas Neon y Better Auth |

---

## 3. Flujo del pipeline

```
CONFIG (configs/<run_id>.yaml)
  - model, lora, data paths, max_steps, metrics, seed
        ↓
1. INGEST / PROCESS
   Entrada: data/raw o data/corpus_*.json
   Salida:  data/processed/{train,val,test}.jsonl
        ↓
2. (OPCIONAL) SEGMENTACIÓN MORFOLÓGICA
   Morfessor / PRPE / FlatCat
   Gate: morphology.enabled en config
        ↓
3. TRAIN
   Base: NLLB-200 o Qwen2.5 + Unsloth | LoRA/QLoRA
   Salida: outputs/<run_id>/ + adapters
        ↓
4. EVALUATE
   chrF++ (principal), BLEU, cosine opcional + plantilla EIB
   Salida: evaluation_report.json
        ↓
5. LOG & PUBLISH
   - Append a data/evaluation_history.json
   - (Futuro) Neon: training_runs, evaluation_samples
   - Regenerar kpi_dashboard.html
```

---

## 4. Contrato de configuración (propuesto)

Archivo: `configs/<run_id>.yaml` (ejemplo conceptual)

```yaml
run_id: "v1.2-qwen-lora-20261017"
seed: 3407

data:
  train: "data/processed/train.jsonl"
  val: "data/processed/val.jsonl"
  test: "data/processed/test.jsonl"

morphology:
  enabled: false
  tool: "morfessor"

model:
  base: "unsloth/Qwen2.5-Coder-7B-Instruct"
  max_seq_length: 2048
  load_in_4bit: true

lora:
  r: 16
  alpha: 16
  dropout: 0.0
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]

train:
  max_steps: 60
  per_device_batch_size: 2
  gradient_accumulation: 4
  learning_rate: 2.0e-4
  warmup_steps: 5
  output_dir: "outputs/v1.2-qwen-lora-20261017"

eval:
  metrics: ["chrf++", "bleu"]
  chrf_word_order: 2
  primary_metric: "chrf++"
  gates:
    chrf_min: 45.0
    bleu_min: 20.0

logging:
  history_file: "data/evaluation_history.json"
```

**Regla:** ningún hiperparámetro “mágico” solo en el código; todo lo variable va en config.

---

## 5. Decisiones técnicas (recomendadas)

| Tema | Decisión | Justificación |
|------|----------|---------------|
| Métrica principal | **chrF++** | Mejor para morfología aglutinante |
| Métrica secundaria | BLEU (subword) | Comparabilidad con literatura |
| Modelo base | NLLB-200 o Qwen2.5 + Unsloth | NLLB orientado a MT; Qwen ya en script |
| Adaptación | LoRA / QLoRA | Bajo VRAM, reproducible |
| Segmentación | Morfessor (opcional) | Mayor ganancia en low-resource agglutinative |
| Splits | train / val / test fijos | Evitar data leakage |
| Seed | Fijo en config | Reproducibilidad |

### Gates de calidad

- Si `chrF++ < gates.chrf_min` → **Requiere ajuste**
- Si ambas métricas cumplen → **Aprobado**
- El histórico siempre se actualiza; el gate solo cambia `result`

---

## 6. Entradas y salidas por etapa

### Process
- Entrada: JSON/JSONL de pares
- Salida: train/val/test.jsonl + estadísticas

### Train
- Entrada: splits + config
- Salida: checkpoint/adaptador en directorio con `run_id` (no sobrescribir runs anteriores)

### Evaluate
- Salida mínima `evaluation_report.json`:
```json
{
  "run_id": "v1.2-qwen-lora-20261017",
  "timestamp": "2026-10-17T12:00:00Z",
  "model_version": "v1.2-Qwen2.5-LoRA",
  "test_pairs": 1250,
  "metrics": { "chrF++": 48.2, "BLEU": 22.4 },
  "gates": { "chrf_min": 45.0, "bleu_min": 20.0, "passed": true },
  "result": "Aprobado"
}
```

### Log
- Append a `data/evaluation_history.json`
- `python scripts/generate_portal.py`

---

## 7. Automatización (el “slot”)

### Local / GPU
```bash
# Ideal (futuro)
python -m wayuunlingo.pipeline run --config configs/v1.2.yaml

# Equivalente actual por etapas
python src/process_data.py
python src/train_model.py
python src/evaluate.py
python scripts/generate_portal.py
```

### Cloud
Mismo comando; solo cambia entorno (GPU, rutas, secretos). Descargar adaptador + report + histórico. No commitear pesos grandes.

---

## 8. Encaje con Neon + pgvector (documental)

Tablas previstas: `training_runs`, `evaluation_samples`, `translation_pairs`, `pair_embeddings`.

- Extensión `vector`
- Source of truth del histórico en esta fase: `evaluation_history.json`
- Neon = siguiente escalón (detalle en docs/NEON.md — paso 2)

---

## 9. Encaje con Auth (documental)

- Better Auth + Google OAuth (patrón cotorr)
- Roles: Admin/ML, Revisor EIB, Usuario final
- No bloquea el pipeline offline; define quién ve métricas en producto

---

## 10. Riesgos y mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Corpus pequeño | Test fijo; gates; evaluación EIB |
| Tokenización distinta entre runs | Documentar en config |
| Pesos en git | Nunca; solo configs + reports + histórico |
| Scripts vs config desalineados | Entrypoint + config obligatorio (fase impl.) |

---

## 11. Criterios de aceptación de este diseño

- [x] Documento único del flujo completo
- [x] Formato de config y de evaluation_report definidos
- [x] Métrica primaria y gates definidos
- [x] Actualización de histórico y dashboard definida
- [x] Encaje futuro Neon/Auth documentado sin forzar implementación

---

## 12. Próximos pasos

1. **Hecho:** este documento
2. `docs/NEON.md`
3. `docs/AUTH.md`
4. Primer run real cuando el corpus esté estable
5. Entrypoint `pipeline run` + tablas Neon si aplica

---

## 13. Referencias internas

- Scripts: `src/process_data.py`, `src/train_model.py`, `src/evaluate.py`
- Histórico: `data/evaluation_history.json`
- Dashboard: `kpi_dashboard.html`, `scripts/generate_portal.py`
- Drive: Software Architecture, Validation Framework
- Neon patrón: `pdf-voice-ai`
- Auth patrón: `cotorr`

---

*Documento de planeación — no sustituye código. Cambios de diseño del pipeline deben actualizarse aquí antes de implementarse.*
