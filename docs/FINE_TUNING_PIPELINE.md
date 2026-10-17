# Wayuunlingo — Pipeline de Fine-Tuning (Planeación v1.0)

**Estado:** Documento de diseño (sin implementación nueva de código)  
**Fecha:** 2026-10-17  
**Objetivo:** Pipeline de fine-tuning reproducible y automatizable (ES↔Wayuunaiki), con métricas chrF++, evaluación EIB y estándares Neon/Auth/Audio.

---

## 1. Propósito

Un flujo controlado: corpus → (morph opcional) → LoRA/QLoRA → evaluate (chrF++) → histórico → dashboard.

**Pipeline listo** = un comando/config produce checkpoint + informe + entrada en histórico.

---

## 2. Flujo

```
CONFIG → PROCESS → [MORPH] → TRAIN → EVALUATE → LOG (JSON → portal; futuro Neon)
```

Incluir **baseline zero-shot** y **dict-RAG** en la batería de evaluación (ver LEGACY_RESOURCES).

---

## 3. Config (ejemplo)

`configs/<run_id>.yaml`: data paths, morphology, model, lora, train steps, eval gates (`chrf_min`, `bleu_min`), logging.

---

## 4. Decisiones técnicas

| Tema | Decisión |
|------|----------|
| Métrica principal | **chrF++** (también por dominio si hay metadata) |
| Secundaria | BLEU |
| Modelo | NLLB-200 o Qwen2.5 + Unsloth |
| Adaptación | LoRA / QLoRA |
| Segmentación | Morfessor/PRPE opcional |
| Baseline fuerte | **Diccionario en prompt (RAG léxico)** antes de reclamar mejora LoRA |

Gates orientativos: chrF++ ≥ 45 y BLEU ≥ 20 → Aprobado (interpretar según dominio del test).

### Lecciones de recursos públicos

- AmericasNLP train es ~**89% diccionario** → no optimizar solo ese dominio.
- En qlora-lab, **dict-RAG ~chrF 19** superó QLoRA solo ~chrF 11.
- Pocas iteraciones a menudo mejor que muchas.
- Prompt de train e inferencia debe ser consistente (con/sin dict).
- Detalle: `docs/LEGACY_RESOURCES.md`.

---

## 5. Datos

| Fuente | Rol |
|--------|-----|
| AmericasNLP 2025 wayuu-spanish | Train/dev público principal |
| Diccionario CSV (qlora-lab) | RAG léxico |
| norgrai/wayuunaiki (Tatoeba) | Secundario |
| Golden set EIB propio | Calidad de producto / cultural |

---

## 6. Automatización

```bash
python -m wayuunlingo.pipeline run --config configs/v1.2.yaml   # futuro
python src/process_data.py && python src/train_model.py && python src/evaluate.py
python scripts/generate_portal.py
```

---

## 7. Encaje

- `NEON.md` — training_runs, translation_pairs  
- `AUTH.md` — Better Auth + Google  
- `AUDIO_STT_TTS.md` — cotorr (voz; no bloquea texto)  
- `LEGACY_RESOURCES.md` — inventario completo  

---

## 8. Próximos pasos

1. Docs de diseño: hechos (pipeline, neon, auth, audio, legacy)  
2. Enlazar descarga AmericasNLP / dict en `data/external/`  
3. Primer run real con config versionada + baseline dict-RAG  
4. Entrypoint unificado + Neon cuando toque implementación  

---

*Documento de planeación — no sustituye código.*
