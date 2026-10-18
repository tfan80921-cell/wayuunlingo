# Ecosistema Wayuu — dos repos, un solo mapa de alcance

**Actualizado:** 2026-10-18  
**Estado acceso:** este documento vive en **wayuunlingo**. El repo **Wayu Engine** aún no es visible para el colaborador `tfan80921-cell` hasta confirmar URL/invite aceptado.

---

## 1. Identidad de cada proyecto

| | **Wayuunlingo** | **Wayu Engine** (propuesto) |
|--|-----------------|-----------------------------|
| **Remoto (confirmado)** | https://github.com/tfan80921-cell/wayuunlingo | *Pendiente: pegar URL exacta* |
| **Rol** | Producto / pipeline MT ES↔Wayuunaiki, evaluación, portal, voz vía cotorr | Motor/plataforma compartida, datos crudos, experimentación pesada, o app “engine” según el otro agente |
| **Stack visto** | Python (process/train/eval), docs, configs YAML, HTML KPIs | *Por inspeccionar* |

Hasta inspeccionar Engine, **no** asumir que duplica train/eval: puede ser frontend, API, corpus store, o el motor de inferencia.

---

## 2. División de alcance (para no hacer lo mismo dos veces)

### Wayuunlingo — dueño de

- Pipeline documentado de **fine-tuning** (config, gates chrF++, histórico).
- Scripts de **process / baseline / eval** públicos del repo.
- **Kanban + cronograma** del trabajo MT.
- Integración documental **Neon / Auth / Audio (cotorr)**.
- Dashboard / portal de KPIs.
- Contrato de datos: JSONL `{source, target, domain?}`.

### Wayu Engine — dueño propuesto (validar al abrir el repo)

- Lo que sea **runtime de producción** o app de usuario si está ahí (API, UI, deploy).
- Experimentos de otro agente que no deban mezclarse con `main` de Lingo.
- Si Engine tiene corpus/train: **una sola fuente de verdad**; el otro repo solo referencia o consume artefactos.

### Compartido (una sola vez)

| Recurso | Dónde vive | Cómo se usa en el otro |
|---------|------------|------------------------|
| AmericasNLP / dict CSV | Disco local + doc en Lingo `data/external/` | Engine enlaza; no re-subir 60k líneas a git |
| Métrica primaria chrF++ | Ambos docs deben decir lo mismo | Misma definición sacrebleu word_order=2 |
| Golden set EIB | Fuera de git / Drive | Ambos leen, ninguno “reinventa” |
| STT/TTS | Patrones **cotorr** | Ambos reutilizan, no forks de audio |

---

## 3. Política de ramas (Wayuunlingo)

| Rama | Uso |
|------|-----|
| `main` | Estable: docs, scripts probados, configs de ejemplo |
| `docs/*` | Solo documentación si el cambio es grande |
| `feat/*` | Código (eval LLM, API, morph) |
| `data/*` | Solo si hay que versionar muestras pequeñas (nunca pesos ni 60k JSONL) |

**Reglas**

1. No trabajar feature grande directo en `main` sin PR cuando haya dos agentes.
2. Un agente = idealmente una rama `feat/<tema>`.
3. Corpora grandes y clones: **gitignore** (ya en Lingo).

### Estado actual Wayuunlingo

- Solo existe **`main`**.
- No crear ramas vacías “por si acaso”; abrir `feat/...` cuando arranque T4b (dict+LLM) u otro trabajo de código.

---

## 4. Coordinación con el otro agente (Wayu Engine)

1. Pegar URL de Engine → inventario de árbol + README.
2. Actualizar esta tabla de alcance con hechos (no supuestos).
3. Si hay solape (p. ej. dos `train_model.py`): decidir **un dueño** y marcar el otro como wrapper o deprecado.
4. Enlazar en ambos README: “Ver también: [otro repo]”.

---

## 5. Checklist inmediato

- [x] Wayuunlingo: commits de diseño + scripts T3/T4 en `main`
- [ ] Wayu Engine: acceso verificado (`owner/repo`)
- [ ] Tabla de alcance cerrada con el otro agente
- [ ] Enlace cruzado README ↔ README
- [ ] Ramas solo cuando haya trabajo paralelo real

---

*Si el invite a Engine fue a otro usuario GitHub (no `tfan80921-cell`), hay que invitar exactamente esa cuenta o pasar el owner del repo.*
