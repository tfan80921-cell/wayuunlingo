# Quality Log - Wayuunlingo

Registro formal de evaluaciones de calidad del sistema de traducción Español ↔ Wayuunaiki.

---

## Convenciones

- Toda evaluación seria debe registrarse aquí.
- Se debe indicar claramente si hubo evaluación humana nativa.
- Las métricas automáticas (chrF++, COMET, BLEU) no sustituyen la validación humana en esta lengua.

---

## Evaluaciones

### 2026-10-20 — Recuperación de calidad (Golden Set v0.2)

- **Acción**: Creación del Golden Set limpio v0.2
- **Motivo**: Los pares anteriores (`corpus_sample.json`) y parte de las métricas históricas no tenían respaldo de calidad suficiente.
- **Dataset**: `data/golden_set/golden_set_v0.2.json` (22 pares)
- **Criterio de inclusión**: Solo formas con respaldo consistente en fuentes abiertas (Omniglot, glosarios de La Guajira, materiales EIB, referencias SIL).
- **Validación nativa**: **Pendiente**
- **Conclusión**: Se congela el uso de los samples antiguos para evaluación seria. Se adopta este set como base de calidad provisional.

---

### Evaluaciones anteriores (histórico del repo)

Los registros previos en `data/evaluation_history.json` (chrF++ 48.2 / BLEU 22.4 etc.) **no cuentan con documentación de evaluación humana nativa** ni desglose por dominio. Se consideran no validados para claims de calidad de producto.

---

## Plantilla para nuevas evaluaciones

```markdown
### YYYY-MM-DD — [Nombre de la evaluación]

- Modelo:
- Dataset de test:
- Número de pares:
- Métricas automáticas:
  - chrF++:
  - COMET:
  - BLEU:
- Evaluación humana:
  - Evaluador(es):
  - Adecuación promedio (1-5):
  - Fluidez promedio (1-5):
  - Observaciones:
- Conclusión:
```
