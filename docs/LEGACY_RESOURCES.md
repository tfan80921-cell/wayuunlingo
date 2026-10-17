# Wayuunlingo — Inventario de recursos legacy y externos

**Fecha:** 2026-10-17  
**Objetivo:** Qué hay disponible, qué se puede reutilizar en Wayuunlingo, y qué no aplica.

---

## 1. Acceso actual (cuenta GitHub `tfan80921-cell`)

| Repo | Tipo | ¿Wayuunaiki? | Reutilizable para Wayuunlingo |
|------|------|--------------|-------------------------------|
| **wayuunlingo** | propio | Sí | Núcleo actual |
| **cotorr** | propio | No (chat voz ES) | **STT/TTS, proxy, resiliencia** → `AUDIO_STT_TTS.md` |
| **pdf-voice-ai** | propio | No | **Neon + pgvector** → `NEON.md` |
| **lawai / lawai2** | propio | No (app legal) | Auth/UI genéricos; **no** corpus ni MT wayuu |
| **binative** | propio | No | No |

**Nota sobre invites:** si los proyectos legacy (Duolingo wayuu, diccionario, chat wayuu) están en **otra cuenta u org**, hay que invitar a `tfan80921-cell` o pasar owner/nombre. En Drive, `Wayuunlingo_Drive` es documentación del proyecto actual, no un segundo corpus grande.

---

## 2. Recursos públicos de alto valor

### 2.1 [asdrubalivan/wayuunaiki-qlora-lab](https://github.com/asdrubalivan/wayuunaiki-qlora-lab)

| Artefacto | Uso en Wayuunlingo |
|-----------|-------------------|
| AmericasNLP 2025 wayuu-spanish (~59k/6.6k) | Corpus base |
| `wayuunaiki_dictionary.csv` | **RAG léxico** |
| Scripts process/eval / dict-augmented | Plantillas |
| Adaptadores Qwen2.5 LoRA (HF) | Solo comparación |
| Resultado clave | **Dict RAG ~chrF 19 > QLoRA solo ~chrF 11** |

Lecciones: corpus ~89% diccionario; no sobre-entrenar; prompt train=inferencia; evaluar por dominio.

HF: `asdrubalivan/wayuunaiki-dataset`, `asdrubalivan/wayuunaiki-qwen25-lora`.

### 2.2 [norgrai/wayuunaiki](https://github.com/norgrai/wayuunaiki)

Bitext Tatoeba ES–guc, BPE, PRPE/FlatCat/Morfessor, POS factors, paper AmericasNLP 2023.

### 2.3 AmericasNLP 2025 shared task

`wayuu-spanish` con dominio (dictionary, bible, books…). Fuente externa versionada; no es el golden set EIB.

---

## 3. Prioridad de adopción

| P | Qué |
|---|-----|
| P0 | Dict RAG + AmericasNLP con dominio |
| P1 | Eval tipo sacrebleu/chrF; morph opcional |
| P2 | Adapters HF solo referencia; Norgrai secundario |

---

## 4. Qué no hacer

- Test solo-diccionario como calidad de producto  
- Miles de steps sin validar chrF  
- Pesos de terceros sin licencia/re-eval  
- Confundir lawai/cotorr con corpus wayuu  

---

## 5. Diseño actualizado

1. Baseline: zero-shot + dict-RAG antes de reclamar mejora LoRA  
2. chrF++ global y por dominio  
3. Golden set EIB propio sigue siendo el diferenciador  

Ver también `FINE_TUNING_PIPELINE.md`.
