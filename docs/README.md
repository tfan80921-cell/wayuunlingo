# Wayuunlingo — Documentación

Índice de diseño (2026-10-17). Prioridad: planeación y estándares del ecosistema; implementación de código solo cuando el corpus y las configs estén estables.

| Documento | Contenido |
|-----------|-----------|
| [FINE_TUNING_PIPELINE.md](./FINE_TUNING_PIPELINE.md) | Slot de fine-tuning: flujo, config YAML, métricas (chrF++), gates |
| [LEGACY_RESOURCES.md](./LEGACY_RESOURCES.md) | Inventario: AmericasNLP, qlora-lab, Norgrai, qué reutilizar |
| [NEON.md](./NEON.md) | NeonDB + pgvector: schema, embeddings, training_runs |
| [AUTH.md](./AUTH.md) | Better Auth + Google OAuth, roles |
| [AUDIO_STT_TTS.md](./AUDIO_STT_TTS.md) | STT/TTS reutilizando **cotorr** |

## Estándares transversales

- **DB:** Neon + `vector` (pdf-voice-ai / cotorr)
- **Auth:** Google vía Better Auth (cotorr)
- **Audio:** WAV, STT dual, TTS fallback (cotorr)
- **MT:** LoRA/QLoRA + **baseline dict-RAG**; chrF++ (idealmente por dominio)

## Artefactos vivos

- `data/evaluation_history.json`
- `python scripts/generate_portal.py`
- Portal / KPIs en Vercel

## Referencias

- `pdf-voice-ai`, `cotorr`, Google Drive (arquitectura / EIB / grants)
- Públicos: AmericasNLP 2025, [wayuunaiki-qlora-lab](https://github.com/asdrubalivan/wayuunaiki-qlora-lab), [norgrai/wayuunaiki](https://github.com/norgrai/wayuunaiki)
