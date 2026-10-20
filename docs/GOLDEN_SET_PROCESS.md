# Proceso de construcción del Golden Set y recuperación de calidad

**Fecha**: 2026-10-19 / 2026-10-20  
**Proyecto**: Wayuunlingo (Español ↔ Wayuunaiki)

---

## 1. Contexto del problema

Se detectó que:

- El archivo `data/corpus_sample.json` contenía pares de baja calidad / incorrectos.
- Las métricas reportadas en `data/evaluation_history.json` (especialmente chrF++ 48.2 y BLEU 22.4) carecían de registro de quién evaluó, con qué criterios y si hubo validación por hablantes nativos.
- En lenguas de muy bajos recursos como el Wayuunaiki, las métricas automáticas sin validación humana son insuficientes y pueden ser engañosas.

Esto motivó un proceso de **contención y reconstrucción de calidad**.

---

## 2. Plan de acción ejecutado

### Fase 0 — Contención
- Se dejó de considerar válido el sample antiguo para evaluación seria.
- Se decidió documentar formalmente el estado de calidad.

### Fase 1 — Construcción de Golden Set limpio
- Se recolectaron formas documentadas de manera consistente en fuentes abiertas.
- Se priorizaron saludos, cortesía, presentaciones y despedidas.
- Se diferenció género solo cuando estaba claramente atestiguado.
- Se generó la **versión 0.2** con 22 pares de confianza alta.

### Fase 2 — Documentación
- Se creó este documento de proceso.
- Se creó `docs/QUALITY_LOG.md` para registrar evaluaciones futuras.
- Se documentó el Golden Set en `data/golden_set/`.

---

## 3. Fuentes principales consultadas

- Omniglot – Useful phrases in Wayuu
- Glosarios y materiales educativos de La Guajira
- Referencias SIL (Diccionario Wayuu / Captain & Captain)
- Materiales de educación bilingüe intercultural (EIB)
- Papers y recursos de AmericasNLP relacionados con Wayuunaiki

---

## 4. Archivos generados en este proceso

| Ruta | Descripción |
|------|-------------|
| `data/golden_set/golden_set_v0.2.json` | Golden Set limpio (22 pares) |
| `data/golden_set/README.md` | Documentación del set |
| `docs/QUALITY_LOG.md` | Registro formal de calidad |
| `docs/GOLDEN_SET_PROCESS.md` | Este documento |

---

## 5. Estado actual y próximos pasos

**Estado actual:**
- Golden Set v0.2 disponible y documentado.
- Validación nativa **pendiente**.
- Métricas históricas anteriores marcadas como no validadas para claims de producto.

**Próximos pasos recomendados:**
1. Validación del Golden Set por al menos 1-2 hablantes nativos o educadores Wayuu.
2. Ampliar el set con dominio escolar / EIB una vez validada la base.
3. Evaluar los modelos actuales **solo** sobre este Golden Set (y registrar resultados en `QUALITY_LOG.md`).
4. Decidir la estrategia de modelo (NLLB destilado + LoRA vs Qwen + LoRA vs dictionary-guided) con base en evaluación real.

---

## 6. Principio rector

> En Wayuunaiki, la calidad se define primero por la validación humana nativa y culturalmente informada. Las métricas automáticas son herramientas de apoyo, no la verdad final.
