# Datos externos (no versionar corpora grandes)

Esta carpeta documenta **fuentes públicas** y cómo traerlas al workspace local.
Los JSONL grandes **no** se suben al repo (ver `.gitignore`).

## 1. Diccionario Wayuunaiki (RAG léxico) — P0

| Campo | Valor |
|-------|--------|
| Origen | [asdrubalivan/wayuunaiki-qlora-lab](https://github.com/asdrubalivan/wayuunaiki-qlora-lab) |
| Archivo | `data/dict/wayuunaiki_dictionary.csv` |
| Uso | Baseline **dict-RAG** (entradas en el prompt antes de reclamar mejora LoRA) |

```bash
# Desde la raíz de wayuunlingo
mkdir -p data/external/dict
curl -L -o data/external/dict/wayuunaiki_dictionary.csv \
  "https://raw.githubusercontent.com/asdrubalivan/wayuunaiki-qlora-lab/main/data/dict/wayuunaiki_dictionary.csv"
```

## 2. AmericasNLP 2025 — wayuu-spanish (guc) — P0

| Campo | Valor |
|-------|--------|
| Repo | [AmericasNLP/americasnlp2025](https://github.com/AmericasNLP/americasnlp2025) |
| Task | ST1 Machine Translation |
| ISO | guc (Wayuunaiki) |
| Tamaños (ref. papers) | train ~59.7k · dev ~6.6k · test ~498 |
| Dominios | dictionary, bible, books, etc. (evaluar **por dominio**) |

```bash
git clone --depth 1 https://github.com/AmericasNLP/americasnlp2025.git data/external/americasnlp2025
# Buscar bajo ST1_MachineTranslation los splits guc / wayuu-spanish
```

También disponible procesado en qlora-lab:

- `data/processed/train.jsonl`, `valid.jsonl`, `test.jsonl`
- HuggingFace: `asdrubalivan/wayuunaiki-dataset`

## 3. norgrai/wayuunaiki (secundario)

Bitext Tatoeba ES–guc, experimentos morph (Morfessor/PRPE/FlatCat).

```bash
git clone --depth 1 https://github.com/norgrai/wayuunaiki.git data/external/norgrai-wayuunaiki
```

## 4. API / búsqueda semántica de referencia

| Repo | Notas |
|------|--------|
| [fredygallego8/wayuulingo-api](https://github.com/fredygallego8/wayuulingo-api) | NestJS + Qdrant + Gemini; búsqueda semántica (no es nuestro corpus, sí patrón vectorial) |

## 5. Golden set EIB (propio)

Sigue siendo **interno / Drive / otro computador**. No sustituir por solo-diccionario AmericasNLP.

## Convención de rutas locales

```
data/external/
  dict/wayuunaiki_dictionary.csv
  americasnlp2025/          # clone
  norgrai-wayuunaiki/       # clone opcional
data/processed/             # salida de process_data.py (train/val/test.jsonl)
```

Tras descargar, el pipeline debe poder apuntar a estas rutas vía `configs/*.yaml`.
