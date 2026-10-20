# Golden Set - Wayuunlingo

## Estado actual

- **Versión activa**: `golden_set_v0.2.json`
- **Fecha de creación**: 2026-10-20
- **Número de pares**: 22
- **Confianza**: Solo pares marcados como **alta**
- **Estado de validación nativa**: Pendiente (aún no revisado por hablantes nativos Wayuu)

## Objetivo

Este Golden Set es el núcleo de calidad para evaluación y fine-tuning de traducción Español ↔ Wayuunaiki.

Prioriza:
- Formas documentadas de manera consistente en fuentes abiertas
- Distinción de género cuando está claramente atestiguada
- Dominios básicos: saludo, cortesía, presentación y despedida

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `golden_set_v0.2.json` | Set limpio y corregido (versión actual) |
| `README.md` | Este archivo |

## Campos del JSON

- `id`: Identificador único
- `spanish`: Texto en español
- `wayuunaiki`: Traducción
- `dominio`: saludo | cortesía | presentación | despedida | básico | escolar
- `genero`: neutral | masculino | femenino | plural
- `registro`: cotidiano | formal | tradicional
- `notas`: Observaciones de uso
- `confianza`: alta | media | baja
- `fuente_aproximada`: Origen de la forma

## Advertencia importante

Este set **aún requiere validación por hablantes nativos** antes de usarse como referencia definitiva de calidad de producto (especialmente para contexto EIB).

Los pares anteriores (`data/corpus_sample.json`) se consideran de baja calidad y no deben usarse para evaluación seria.

## Próximos pasos

1. Validación nativa (1-2 hablantes / educadores Wayuu)
2. Ampliación con dominio escolar / EIB
3. Registro de evaluación humana en `docs/QUALITY_LOG.md`
