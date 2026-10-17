# Wayuunlingo — Inventario de recursos legacy y externos

**Fecha:** 2026-10-17 (actualizado)  
**Objetivo:** Qué hay disponible, qué se puede reutilizar, y cómo traerlo a `data/external/`.

---

## 1. Acceso cuenta GitHub `tfan80921-cell`

| Repo | ¿Wayuunaiki? | Reutilizable |
|------|--------------|--------------|
| **wayuunlingo** | Sí | Núcleo |
| **cotorr** | No (voz ES) | STT/TTS, proxy → `AUDIO_STT_TTS.md` |
| **pdf-voice-ai** | No | Neon + pgvector → `NEON.md` |
| **lawai / lawai2** | No (legal) | Auth/UI genéricos; **no** corpus wayuu |
| **binative** | No | No |

Si hay repos legacy (Duolingo wayuu, diccionario propio, chat) en **otra cuenta/org**, deben ser visibles para `tfan80921-cell` (colaborador o público). Mientras tanto el valor operativo está en los recursos públicos de la sección 2.

---

## 2. Recursos públicos de alto valor

### 2.1 [asdrubalivan/wayuunaiki-qlora-lab](https://github.com/asdrubalivan/wayuunaiki-qlora-lab)

| Artefacto | Uso |
|-----------|-----|
| AmericasNLP procesado (train/valid/test jsonl) | Corpus base |
| `data/dict/wayuunaiki_dictionary.csv` (~2k entradas) | **RAG léxico** |
| Scripts dict-augmented / evaluate | Plantillas |
| Resultado clave | **Dict RAG ~chrF 19 > QLoRA solo ~chrF 11** |

Descarga dict (también documentada en `data/external/README.md`):

```bash
curl -L -o data/external/dict/wayuunaiki_dictionary.csv \
  "https://raw.githubusercontent.com/asdrubalivan/wayuunaiki-qlora-lab/main/data/dict/wayuunaiki_dictionary.csv"
```

### 2.2 [AmericasNLP/americasnlp2025](https://github.com/AmericasNLP/americasnlp2025)

ST1 MT; guc ~59.7k train / ~6.6k dev / ~498 test. Dominios (dictionary, bible, books…). **Evaluar por dominio.**

### 2.3 [norgrai/wayuunaiki](https://github.com/norgrai/wayuunaiki)

Tatoeba ES–guc, morph (Morfessor/PRPE/FlatCat).

### 2.4 [fredygallego8/wayuulingo-api](https://github.com/fredygallego8/wayuulingo-api)

NestJS + **Qdrant** + Gemini: búsqueda semántica Wayuunaiki. No es nuestro corpus; sí referencia de **API + vectores** (complementa Neon/pgvector).

---

## 3. Rutas locales (repo wayuunlingo)

| Ruta | Contenido |
|------|-----------|
| `data/external/README.md` | Instrucciones de clone/curl |
| `data/external/dict/` | CSV diccionario (gitignored el CSV) |
| `configs/baseline_dict_rag.yaml` | Config baseline sin LoRA |
| `configs/example_lora.yaml` | Config ejemplo fine-tuning |

---

## 4. Prioridad

| P | Qué |
|---|-----|
| P0 | Dict en `data/external/dict` + baseline dict-RAG |
| P0 | AmericasNLP / processed jsonl + eval por dominio |
| P1 | Scripts eval alineados a sacrebleu/chrF |
| P2 | Norgrai morph; adapters HF solo referencia |

---

## 5. Qué no hacer

- Test solo-diccionario como calidad de producto EIB  
- Miles de steps sin validar chrF  
- Pesos de terceros sin licencia/re-eval  
- Confundir lawai/cotorr con corpus wayuu  

---

## 6. Diseño

1. Baseline zero-shot + **dict-RAG** antes de reclamar mejora LoRA  
2. chrF++ global y por dominio  
3. Golden set EIB propio = diferenciador de producto  

Ver `FINE_TUNING_PIPELINE.md` y `data/external/README.md`.
