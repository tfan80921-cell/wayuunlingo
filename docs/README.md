# Wayuunlingo — Documentación

Índice de diseño (2026-10-17).

| Documento | Contenido |
|-----------|-----------|
| [FINE_TUNING_PIPELINE.md](./FINE_TUNING_PIPELINE.md) | Slot fine-tuning, config, chrF++, gates |
| [LEGACY_RESOURCES.md](./LEGACY_RESOURCES.md) | Oro público: AmericasNLP, qlora-lab, Norgrai |
| [CRONOGRAMA.md](./CRONOGRAMA.md) | 8 semanas + hitos M1–M5 |
| [KANBAN.md](./KANBAN.md) | Done / To Do T1–T11 / Backlog |
| [NEON.md](./NEON.md) | Neon + pgvector |
| [AUTH.md](./AUTH.md) | Better Auth + Google |
| [AUDIO_STT_TTS.md](./AUDIO_STT_TTS.md) | Voz vía cotorr |

## Estándares

- **DB:** Neon + vector · **Auth:** Better Auth · **Audio:** cotorr  
- **MT:** LoRA + **baseline dict-RAG** · chrF++ por dominio cuando haya metadata  

## Datos externos

Ver `data/external/README.md` y configs:

- `configs/baseline_dict_rag.yaml`
- `configs/example_lora.yaml`

## Próximo trabajo operativo

Kanban **T1 → T4** (dict + AmericasNLP + baseline medible). No abrir Duolingo/chat hasta cerrar baseline.
