# Wayuunlingo — Audio: STT / TTS (basado en cotorr)

**Estado:** Documentación de diseño  
**Fecha:** 2026-10-17  
**Base de referencia:** repositorio **cotorr** (Spot AI) — STT dual, TTS neural, fallbacks y UI de voz.

---

## 1. Propósito

La tradición wayuu es **fuertemente oral**. El traductor no puede quedarse solo en texto:

- **STT:** usuario habla en español o Wayuunaiki → texto  
- **Motor MT:** texto origen → texto destino (pipeline Wayuunlingo)  
- **TTS:** texto destino → audio  

Diseño de esa capa **reutilizando cotorr**, sin reescribir el stack de audio desde cero.

---

## 2. Qué se reutiliza de cotorr

| Pieza en cotorr | Rol | Reuso en Wayuunlingo |
|-----------------|-----|----------------------|
| Web Speech API (live) | Transcripción en vivo | Primera vía STT |
| Captura mic + encodeWAV | Audio PCM estable | Mismo pipeline de captura |
| POST /api/transcribe | STT servidor (ladder) | Segunda vía si Web Speech falla |
| POST /api/tts | TTS neural + caché | Voz de la traducción |
| Fallback TTS navegador | Si la API falla | Offline / degradación |
| Ladder (backoff, failover) | Resiliencia | Mismos principios en proxy |
| Voice call modal (UX) | Conversación continua | Modo diálogo ES ↔ Wayuunaiki |

**Principio:** las claves de APIs de voz **no van al navegador**; todo proxy en servidor.

---

## 3. Flujo objetivo

```
Micrófono/teclado → STT → Texto origen → MT → Texto destino → TTS → Altavoz
```

### Turno de voz típico

1. Usuario pulsa mic (o modo llamada).  
2. Cliente: captura + (opcional) hipótesis live Web Speech.  
3. Si hace falta: WAV → `/api/transcribe` → texto origen.  
4. Motor de traducción (LoRA / servicio MT).  
5. Texto destino → `/api/tts` → reproducción.  
6. (Modo diálogo) reabrir escucha tras TTS.

### Solo texto

Camino principal del pipeline de fine-tuning y uso sin micrófono.

---

## 4. Realidad low-resource (Wayuunaiki)

| Escenario | Estrategia v1 | Posterior |
|-----------|---------------|----------|
| Habla **español** | STT ES → MT → TTS | — |
| Habla **Wayuunaiki** | Intentar STT; si falla, texto o puente ES | Corpus oral + adaptadores |
| Reproducir **Wayuunaiki** | TTS genérico (limitado) o texto destacado | TTS con datos wayuu |

UI: marcar modo voz Wayuunaiki como **experimental** hasta evaluación EIB de audio.

---

## 5. Endpoints propuestos

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/transcribe` | Audio → `{ text }` |
| POST | `/api/tts` | `{ text, voice?, lang? }` → audio |
| POST | `/api/translate` | `{ text, source_lang, target_lang }` → traducción |
| GET | `/api/health` | Estado de claves y DB |

---

## 6. Cliente

- `getUserMedia`, silencio → fin de turno (~1.5–2 s)  
- Estados: escuchando / traduciendo / hablando  
- Offline: texto + Web Speech si el navegador lo permite  

---

## 7. Seguridad y coste

- Rate limit en transcribe/tts.  
- Auth o API key en producción (`docs/AUTH.md`).  
- No loguear audio crudo sin política de privacidad.  
- Caché TTS para frases frecuentes.

---

## 8. Relación con fine-tuning

Pipeline `process` / `train` / `evaluate` = **texto**.  
Métricas actuales: chrF++, BLEU.  
Audio no bloquea el slot de fine-tuning.

---

## 9. Plan de implementación (cuando toque código)

1. Adaptar de cotorr: WAV, transcribe, tts, fallbacks.  
2. STT → translate → TTS.  
3. UI mínima: mic + texto + play.  
4. Limitaciones Wayuunaiki visibles en UI.  
5. Set pequeño de frases orales con revisores EIB.

---

## 10. Criterios de aceptación (diseño)

- [x] Base: cotorr.  
- [x] Flujo STT → MT → TTS definido.  
- [x] Estrategia sin soporte nativo Wayuunaiki documentada.  
- [x] Separación pipeline texto vs capa audio.  
- [x] Auth/coste referidos a AUTH.

---

## 11. Referencias

- `cotorr`: docs/ARCHITECTURE.md, audioService, /api/tts, /api/transcribe  
- Wayuunlingo: FINE_TUNING_PIPELINE.md, AUTH.md, NEON.md  
