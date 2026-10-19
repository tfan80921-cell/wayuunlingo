# Estándar KPI — Prometheus + Grafana (todos los proyectos)

**Versión:** 1.0 · 2026-10-19  
**Objetivo:** Un mismo contrato de métricas y eventos en **Wayuunlingo**, **cotorr**, **pdf-voice-ai**, **wayuu-engine** y futuros sistemas. Sin inventar un stack distinto por repo.

Basado en el modelo de 4 pilares (costo / uso técnico / negocio / calidad) y evento estructurado por interacción.

---

## 1. Principios

1. **Un evento estructurado por unidad de trabajo** (chat, traducción, request API) — no logs sueltos sin schema.
2. **Prometheus** = series numéricas (contadores, histogramas, gauges) para paneles y alertas.
3. **Logs estructurados (Loki u opcional)** = detalle del mismo evento para drill-down.
4. Empezar con **3 KPIs** por servicio; ampliar después.
5. Labels estables: `project`, `service`, `agent_id` (si aplica), `model` — evitar alta cardinalidad (`client_id` **no** va en labels de Prometheus).

---

## 2. Cuatro pilares (nombres canónicos)

### 2.1 Costo

| Métrica / campo | Tipo | Descripción |
|-----------------|------|-------------|
| `tokens_input`, `tokens_output` | en evento + counters | Por modelo |
| `cost_usd` | en evento + counter | Costo de la unidad |
| `kpi_cost_usd_total` | Counter | Labels: `project`, `service`, `model`, `provider` |

Derivados en Grafana: `costo_por_chat`, `% costo por proveedor`.

### 2.2 Uso técnico

| Métrica | Tipo | Labels sugeridos |
|---------|------|------------------|
| `kpi_requests_total` | Counter | `project`, `service`, `status` |
| `kpi_request_duration_seconds` | Histogram | `project`, `service` |
| `kpi_errors_total` | Counter | `project`, `service`, `error_type` |
| `kpi_tool_calls_total` | Counter | `project`, `service`, `tool` |
| `kpi_model_requests_total` | Counter | `project`, `model` |

### 2.3 Negocio

| Campo evento / métrica | Notas |
|------------------------|--------|
| `resolved`, `human_handoff` | Boolean en evento |
| `kpi_resolved_total` / `kpi_handoff_total` | Counters |
| `client_id` | Solo en **log/evento**, nunca como label Prometheus |
| Horas humanas ahorradas | Calculado en dashboard (no hace falta en el agente) |

### 2.4 Calidad

| Campo / métrica | Notas |
|-----------------|--------|
| `client_feedback` (-1/0/1 o 1–5) | En evento + counter opcional |
| En MT (Wayuunlingo / Engine): `chrf`, `bleu` | Gauges o summary por `run_id` / batch, no por request de usuario si es batch |

---

## 3. Contrato del evento (JSON)

Emitir **al cerrar** cada chat / request / job:

```json
{
  "timestamp": "2026-10-18T22:00:00Z",
  "project": "cotorr",
  "service": "chat_api",
  "agent_id": "ventas_whatsapp",
  "client_id": "hash_opcional",
  "model": "gpt-4o-mini",
  "provider": "openai",
  "tokens_in": 850,
  "tokens_out": 320,
  "cost_usd": 0.0042,
  "latency_ms": 2100,
  "tool_calls": 2,
  "resolved": true,
  "human_handoff": false,
  "client_feedback": 1,
  "status": "ok"
}
```

Campos extra por dominio:

| Proyecto | Extra |
|----------|--------|
| wayuunlingo / wayuu-engine | `direction` (es_guc), `domain`, `chrf`, `run_id` |
| pdf-voice-ai | `rack_id`, `pages`, `mode` (tts/stt/pdf) |
| cotorr | `channel` (web/whatsapp), `session_id` hasheado |

---

## 4. Prometheus — nombres de métricas (prefijo `kpi_`)

```text
kpi_requests_total{project,service,status}
kpi_request_duration_seconds{project,service}     # histogram
kpi_cost_usd_total{project,service,model,provider}
kpi_tokens_total{project,service,model,direction} # direction=in|out
kpi_errors_total{project,service,error_type}
kpi_tool_calls_total{project,service,tool}
kpi_resolved_total{project,service}
kpi_handoff_total{project,service}
kpi_feedback_total{project,service,value}         # value=up|down|neutral
```

**Endpoint:** `GET /metrics` (o sidecar) en cada servicio.  
**Scraping:** Prometheus / Grafana Alloy → Grafana Cloud (`metrics:write`).

---

## 5. Implementación mínima (empezar esta semana)

Por servicio, solo **3** números al principio:

1. `costo_por_request` → `kpi_cost_usd_total` + count de requests  
2. `clientes_o_requests_atendidos` → `kpi_requests_total`  
3. `tasa_resolucion` → `kpi_resolved_total / kpi_requests_total`  

Instrumentar **un** flujo primero (ej. un agente WhatsApp en cotorr, o `POST /translate` cuando exista).

### Python (esqueleto)

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUESTS = Counter("kpi_requests_total", "Requests", ["project", "service", "status"])
COST = Counter("kpi_cost_usd_total", "Cost USD", ["project", "service", "model", "provider"])
LATENCY = Histogram("kpi_request_duration_seconds", "Latency", ["project", "service"])

def record_kpi(*, project, service, model, provider, cost_usd, latency_s, status="ok"):
    REQUESTS.labels(project, service, status).inc()
    COST.labels(project, service, model, provider).inc(cost_usd)
    LATENCY.labels(project, service).observe(latency_s)
```

### Node / TypeScript (idea)

Misma semántica con `prom-client`: counters + histogram; log JSON del evento al cerrar el chat.

---

## 6. Grafana — paneles base

| Panel | Query (idea) |
|-------|----------------|
| $$$ por proyecto/servicio | `sum(rate(kpi_cost_usd_total[1h])) by (project, service)` |
| Costo por request | `sum(rate(kpi_cost_usd_total[1h])) / sum(rate(kpi_requests_total[1h]))` |
| Latencia p95 | `histogram_quantile(0.95, sum(rate(kpi_request_duration_seconds_bucket[5m])) by (le, project))` |
| Errores | `sum(rate(kpi_errors_total[5m])) by (project, service)` |
| Resolución | `sum(rate(kpi_resolved_total[1h])) / sum(rate(kpi_requests_total{status="ok"}[1h]))` |

Variable de dashboard: `project` (y `service` / `agent_id` si aplica).

ROI (negocio): definir en el panel el costo humano de referencia (ej. USD/hora) como constante; no hardcodear en cada repo.

---

## 7. Mapa por repositorio

| Repo | `project` label | Primer punto de instrumentación |
|------|-----------------|----------------------------------|
| cotorr | `cotorr` | Fin de turno de chat / voice call |
| wayuunlingo | `wayuunlingo` | Eval batch + futuro `/translate` |
| wayuu-engine | `wayuu_engine` | Pipeline train/infer (ya hay mención Prometheus en Engine) |
| pdf-voice-ai | `pdf_voice_ai` | Fin de job PDF / chat voz |

**No duplicar** exportadores: un `/metrics` por proceso; Alloy/Prometheus scrapea todos.

---

## 8. Relación con KPIs de MT (Wayuunlingo)

`data/evaluation_history.json` y el portal HTML siguen siendo el **histórico de modelos** (chrF++, EIB).  
Prometheus no sustituye eso: complementa con **costo/latencia/uso en runtime**.  
Opcional: al cerrar un `evaluate.py`, emitir también un evento `kpi` con `chrf`, `run_id`.

---

## 9. Checklist de adopción

- [ ] Definir `project` + `service` en cada repo (README o este doc)
- [ ] Dependencia `prometheus_client` / `prom-client`
- [ ] Endpoint `/metrics`
- [ ] `record_kpi` al final del path crítico
- [ ] Log JSON del evento completo
- [ ] Scrape en Alloy/Prometheus
- [ ] Dashboard Grafana con variable `project`
- [ ] Solo 3 KPIs al inicio por servicio

---

## 10. Próximo paso concreto

1. Elegir **un** servicio piloto (recomendado: **cotorr** chat, o Engine si ya exporta Prometheus).  
2. Pegar el esqueleto de métricas + un panel en Grafana Cloud.  
3. Replicar el mismo contrato en Wayuunlingo cuando exista API de traducción.

Si indicas stack exacto del piloto (Python FastAPI, Bun/Node cotorr, etc.), el siguiente entregable puede ser el archivo de métricas listo para merge en ese repo.
