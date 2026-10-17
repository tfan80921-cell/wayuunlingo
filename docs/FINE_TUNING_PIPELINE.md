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
        ↓
1. INGEST / PROCESS → data/processed/{train,val,test}.jsonl
        ↓
2. (OPCIONAL) SEGMENTACIÓN MORFOLÓGICA (Morfessor / PRPE)
        ↓
3. TRAIN (NLLB o Qwen2.5 + Unsloth, LoRA/QLoRA) → outputs/<run_id>/
        ↓
4. EVALUATE (chrF++ principal, BLEU, EIB humano)
        ↓
5. LOG → evaluation_history.json → generate_portal.py
         (futuro: training_runs en Neon)
```

---

## 4. Contrato de configuración (propuesto)

Archivo: `configs/<run_id>.yaml`

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
train:
  max_steps: 60
  per_device_batch_size: 2
  gradient_accumulation: 4
  learning_rate: 2.0e-4
  output_dir: "outputs/v1.2-qwen-lora-20261017"
eval:
  metrics: ["chrf++", "bleu"]
  primary_metric: "chrf++"
  gates:
    chrf_min: 45.0
    bleu_min: 20.0
logging:
  history_file: "data/evaluation_history.json"
```

**Regla:** ningún hiperparámetro “mágico” solo en el código; todo lo variable va en config.

---

## 5. Decisiones técnicas

| Tema | Decisión |
|------|----------|
| Métrica principal | **chrF++** |
| Secundaria | BLEU |
| Modelo base | NLLB-200 o Qwen2.5 + Unsloth |
| Adaptación | LoRA / QLoRA |
| Segmentación | Morfessor opcional |
| Splits | train/val/test fijos |
| Seed | Fijo en config |

Gates: chrF++ ≥ 45 y BLEU ≥ 20 → Aprobado; si no → Requiere ajuste.

---

## 6. Entradas / salidas

- **Process:** JSON/JSONL → train/val/test.jsonl  
- **Train:** splits + config → adaptador en `outputs/<run_id>/`  
- **Evaluate:** `evaluation_report.json` con métricas, gates, result  
- **Log:** append a `evaluation_history.json` + `python scripts/generate_portal.py`

---

## 7. Automatización (el “slot”)

```bash
# Ideal (futuro)
python -m wayuunlingo.pipeline run --config configs/v1.2.yaml

# Por etapas (hoy)
python src/process_data.py && python src/train_model.py && python src/evaluate.py
python scripts/generate_portal.py
```

Cloud GPU: mismo comando; no commitear pesos grandes.

---

## 8. Encaje con Neon + Auth + Audio (documental)

Ver:

- `docs/NEON.md` — tablas `training_runs`, `translation_pairs`, pgvector  
- `docs/AUTH.md` — Better Auth + Google, roles  
- `docs/AUDIO_STT_TTS.md` — STT/TTS desde cotorr (no bloquea el pipeline texto)

---

## 9. Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Corpus pequeño | Test fijo; gates; EIB |
| Tokenización distinta entre runs | Documentar en config |
| Pesos en git | Nunca |
| Scripts vs config | Entrypoint unificado (fase impl.) |

---

## 10. Criterios de aceptación de este diseño

- [x] Flujo completo documentado  
- [x] Config y evaluation_report definidos  
- [x] Métrica primaria y gates  
- [x] Histórico y dashboard  
- [x] Neon / Auth / Audio enlazados sin forzar implementación

---

## 11. Próximos pasos

1. **Hecho:** FINE_TUNING_PIPELINE.md  
2. **Hecho:** NEON.md  
3. **Hecho:** AUTH.md  
4. **Hecho:** AUDIO_STT_TTS.md  
5. Corpus estable → primer run real con config versionada  
6. Entrypoint `pipeline run` + tablas Neon + API STT/MT/TTS cuando toque código

---

## 12. Referencias

- Scripts: `src/process_data.py`, `src/train_model.py`, `src/evaluate.py`  
- Histórico: `data/evaluation_history.json`  
- Índice: `docs/README.md`  
- Drive: Architecture, Validation Framework  
- `pdf-voice-ai` (Neon), `cotorr` (Auth + Audio)

---

*Documento de planeación — no sustituye código. Cambios de diseño del pipeline deben actualizarse aquí antes de implementarse.*
