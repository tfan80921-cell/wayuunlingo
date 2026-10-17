# Wayuunlingo

**Motor de traducción IA Español ↔ Wayuunaiki**  
Proyecto open-source, offline-first, orientado a la preservación y revitalización de la lengua Wayuu.

## Descripción

Wayuunlingo es un pipeline completo de machine translation para el par de idiomas **Español ↔ Wayuunaiki** (lengua indígena de La Guajira, Colombia/Venezuela). Utiliza técnicas de fine-tuning eficiente (LoRA / QLoRA con Unsloth) sobre modelos multilingües base y está diseñado para ejecutarse offline en dispositivos de bajo recurso mediante cuantización (llama.cpp / ONNX).

## Estructura del repositorio

```
wayuunlingo/
├── data/
│   ├── corpus_sample.json          # Pares de ejemplo ES-WAY
│   └── evaluation_history.json     # Registro histórico de KPIs
├── src/
│   ├── process_data.py             # Pipeline de estructuración de datos
│   ├── train_model.py              # Fine-tuning con Unsloth + LoRA
│   └── evaluate.py                 # Evaluación chrF++ / BLEU
├── kpi_dashboard.html              # Dashboard visual de KPIs
└── README.md
```

## Métricas objetivo

| Métrica              | Meta   | Estado actual (v1.2) |
|----------------------|--------|----------------------|
| chrF++               | ≥ 45.0 | **48.2** ✅          |
| BLEU (subpalabras)   | ≥ 20.0 | **22.4** ✅          |
| Adecuación EIB       | ≥ 4.0  | **4.2 / 5.0** ✅     |

## Uso rápido

```bash
# Procesar datos
python src/process_data.py

# Entrenar (requiere GPU + Unsloth)
python src/train_model.py

# Evaluar
python src/evaluate.py
```

Abre `kpi_dashboard.html` en cualquier navegador para ver el panel de resultados.

## Principios

- **Offline-first**: modelos cuantizados para uso sin internet en zonas rurales.
- **Soberanía cultural**: corpus y modelos bajo licencia abierta con atribución a la comunidad Wayuu.
- **Co-creación**: feedback loop con educadores EIB y hablantes nativos.

## Licencia

Open Source — uso libre con atribución a la comunidad Wayuu y al proyecto Wayuunlingo.
