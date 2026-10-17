# Wayuunlingo — Documentación

Índice de diseño (2026-10-17). Prioridad: planeación y estándares del ecosistema; implementación de código solo cuando el corpus y las configs estén estables.

| Documento | Contenido |
|-----------|-----------|
| [FINE_TUNING_PIPELINE.md](./FINE_TUNING_PIPELINE.md) | Slot de fine-tuning: flujo, config YAML, métricas (chrF++), gates, automatización |
| [NEON.md](./NEON.md) | NeonDB + pgvector: schema previsto, embeddings, training_runs |
| [AUTH.md](./AUTH.md) | Better Auth + Google OAuth, roles (admin / reviewer_eib / user) |
| [AUDIO_STT_TTS.md](./AUDIO_STT_TTS.md) | STT/TTS reutilizando **cotorr**; flujo voz → MT → voz |

## Estándares transversales

- **DB:** Neon + extensión `vector` (mismo criterio que pdf-voice-ai y cotorr).
- **Auth:** Google vía Better Auth (patrón cotorr).
- **Audio:** Captura WAV, STT dual, TTS con fallback (patrón cotorr).
- **MT:** Pipeline texto documentado; LoRA/QLoRA; evaluación con chrF++.

## Artefactos vivos

- Histórico de métricas: `data/evaluation_history.json`
- Regenerar dashboard: `python scripts/generate_portal.py`
- Portal / KPIs desplegados en Vercel (ver README raíz del repo)

## Referencias externas al monorepo mental

- `pdf-voice-ai` → Neon bootstrap  
- `cotorr` → Auth, STT/TTS, resiliencia de APIs  
- Google Drive → arquitectura, UI/UX, validation framework, grants  
