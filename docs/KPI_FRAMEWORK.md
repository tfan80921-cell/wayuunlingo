# Framework de KPIs — de demo a producto medible

**Versión:** 1.0 · 2026-10-19  
**Ámbito:** todos los productos del ecosistema (Cotorr/Spot, Wayuunlingo, Wayu Engine, pdf-voice-ai, llm-gateway).  
**Idioma del contrato:** labels y nombres de métricas en inglés estable; este doc en español para el equipo.

Este documento **consolida y valida** el modelo de 3 capas (pilares → captura → dashboard) y lo alinea con lo ya construido: Prometheus en Cotorr, plan LiteLLM multi-sitio, y estándar transversal en este repo.

---

## 1. Por qué importa

Sin KPIs de **costo + negocio**, un agente es una demo. Con ellos puedes:

- Ver qué flujo quema dinero (modelo / proveedor / agente).
- Demostrar ROI frente a atención humana.
- Decidir fallbacks free (LiteLLM) vs rutas de pago.
- Priorizar calidad (CSAT, correcciones) sin adivinar.

---

## 2. Arquitectura de observación (quién mide qué)

```text
┌─────────────────────────────────────────────────────────────┐
│  Producto (Cotorr, Wayuunlingo, Engine…)                      │
│  • Evento estructurado al cerrar chat / job                   │
│  • Prometheus /metrics → negocio, latencia total, resolved    │
└────────────────────────────┬────────────────────────────────┘
                             │ OpenAI-compatible
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  LiteLLM (llm-gateway) — local | AWS | réplica                │
│  • tokens reales, costo técnico, cascada, modelo usado        │
└────────────────────────────┬────────────────────────────────┘
                             ▼
                    Groq / Gemini / OpenRouter / …
                             │
                             ▼
              Grafana Cloud (Alloy: metrics + logs)
```

| Dato | Fuente de verdad |
|------|------------------|
| Tokens in/out, costo LLM por modelo/proveedor | **LiteLLM** (spend) |
| Latencia punta a punta, resolved, handoff, errores de app | **Producto** `/metrics` + evento JSON |
| Ingresos, conversión, plan del cliente | **Billing de producto** (futuro) |

**No duplicar** el panel de “$$$ LLM” sumando costo estimado en la app **y** LiteLLM. Un solo panel primario de costo técnico = gateway.

Repos relacionados:

| Repo | Doc |
|------|-----|
| [llm-gateway](https://github.com/tfan80921-cell/llm-gateway) | Multi-sitio LiteLLM |
| [cotorr](https://github.com/tfan80921-cell/cotorr) | `docs/KPI.md`, `docs/LLM_GATEWAY_PLAN.md`, `/metrics` |
| wayuunlingo | Este archivo + `docs/KPI_PROMETHEUS_GRAFANA.md` |

---

## 3. Capa 1 — Los cuatro pilares (qué medir)

### 3.1 COSTO

| KPI / campo | Descripción | Fuente típica |
|-------------|-------------|---------------|
| `tokens_in` / `tokens_out` | Por request y agregados por modelo | LiteLLM |
| `cost_usd` | Costo de la unidad de trabajo | LiteLLM (real) o estimado solo si no hay gateway |
| `costo_por_chat` | Suma costo LLM (+ embeddings/tools si aplica) | Derivado |
| `costo_por_cliente` | `sum(cost) / clientes_unicos` | Grafana |
| `costo_por_agente` | Por `agent_id` (ventas vs soporte) | Labels / evento |
| `% costo por proveedor` | Groq, Gemini, OpenRouter, … | LiteLLM |

### 3.2 USO TÉCNICO

| KPI | Descripción |
|-----|-------------|
| `total_chats` / requests | Volumen |
| `mensajes_por_chat` | Profundidad de conversación |
| `latency_ms` / p95 | Experiencia percibida (app) |
| `tasa_error` | Fallos de app o upstream agotado |
| `tasa_fallback_a_humano` | `human_handoff` |
| `tool_calls` | MCP, búsqueda, etc. |
| `modelo_usado` | Modelo efectivo (post-cascada) |

### 3.3 NEGOCIO (lo que vende)

| KPI | Descripción |
|-----|-------------|
| `clientes_atendidos_unicos` | Identificador hasheado, **nunca** en label Prometheus de alta cardinalidad |
| `tiempo_promedio_resolucion` | Vs baseline humano |
| `tasa_resolucion_autonoma` | `% resolved && !human_handoff` |
| `tasa_conversion` | Si el flujo es ventas |
| `horas_humanas_ahorradas` | `chats × tiempo_humano_promedio` (constante de negocio en Grafana) |

### 3.4 CALIDAD

| KPI | Descripción |
|-----|-------------|
| CSAT / `client_feedback` | -1 / 0 / 1 o escala 1–5 |
| % corregidas por humano | Handoff + edición |
| Dominio MT (Wayuunlingo/Engine) | chrF++, golden EIB (histórico de eval, no solo runtime) |

---

## 4. Capa 2 — Cómo capturarlo (sin volverse loco)

### 4.1 Un evento estructurado por unidad de trabajo

Al **cerrar** chat, turno relevante o job:

```json
{
  "type": "kpi_chat",
  "timestamp": "2026-10-19T12:00:00Z",
  "project": "cotorr",
  "service": "chat_api",
  "agent_id": "ventas_whatsapp",
  "client_id": "hash_opcional",
  "model": "chat-free",
  "provider": "groq",
  "tokens_in": 850,
  "tokens_out": 320,
  "cost_usd": 0.0042,
  "latency_ms": 2100,
  "tool_calls": 2,
  "resolved": true,
  "human_handoff": false,
  "client_feedback": 1,
  "status": "ok",
  "gateway": true
}
```

Reglas:

1. **Log JSON** (Loki / drain) = detalle y drill-down.  
2. **Prometheus** = contadores/histogramas con labels de **baja cardinalidad**: `project`, `service`, `agent_id`, `model`, `provider`, `status`.  
3. **No** pongas `client_id` ni texto libre en labels de Prometheus.

### 4.2 Métricas Prometheus canónicas (`kpi_*`)

```text
kpi_requests_total{project,service,status}
kpi_request_duration_seconds{project,service}          # histogram
kpi_cost_usd_total{project,service,model,provider}   # solo si la app es fuente; preferir LiteLLM para $$$ LLM
kpi_tokens_total{project,service,model,direction}    # idem
kpi_errors_total{project,service,error_type}
kpi_tool_calls_total{project,service,tool}
kpi_resolved_total{project,service}
kpi_handoff_total{project,service}
kpi_feedback_total{project,service,value}
```

**Cotorr (ya):** `GET /metrics` + log `type=kpi_chat` en `/api/chat`.  
Con LiteLLM activo, el panel de costo LLM prioritario pasa al gateway; Cotorr mantiene volumen, latencia total y resolved.

### 4.3 Pipeline hacia Grafana

1. Producto expone `/metrics` y logs JSON.  
2. **Grafana Alloy** (o agent) con `metrics:write` + `logs:write`.  
3. LiteLLM: scrape de sus métricas/spend según despliegue (`llm-gateway` local/AWS/réplica).  
4. Dashboards con variable `project` y, si aplica, `agent_id`.

---

## 5. Capa 3 — Dashboard que “da plata”

### Mínimo viable (empezar con 3)

1. **Costo por chat / request** (técnico desde LiteLLM; o estimado solo en dev sin gateway).  
2. **Clientes o requests atendidos** (`kpi_requests_total`).  
3. **Tasa de resolución** (`kpi_resolved_total / kpi_requests_total`).

### Paneles siguientes

| Panel | Idea de query |
|-------|----------------|
| $$$ por agente | `sum(rate(kpi_cost_usd_total[1h])) by (agent_id)` o spend LiteLLM por key/modelo |
| Costo por cliente | `sum(cost) / count distinct client` (desde logs, no labels) |
| Latencia p95 | `histogram_quantile(0.95, … kpi_request_duration_seconds_bucket)` |
| ROI | Constante Grafana: costo humano/hora ÷ clientes/hora vs costo IA/cliente |

**ROI ejemplo de narrativa comercial:**  
Si humano = 0,30 USD/cliente y IA = 0,01 USD/cliente → ~30× ahorro. Ese número se enseña al cliente final; se calcula en dashboard, no hace falta hardcodearlo en cada repo.

---

## 6. Mapa por proyecto

| Proyecto | `project` label | Primer path a instrumentar | Costo LLM |
|----------|-----------------|----------------------------|-----------|
| cotorr | `cotorr` | `/api/chat` (hecho baseline) | → LiteLLM |
| llm-gateway | `llm_gateway` | spend LiteLLM nativo | Nativo |
| wayuunlingo | `wayuunlingo` | eval batch + futuro translate | Gateway cuando exista API |
| wayuu-engine | `wayuu_engine` | infer/train según repo | Alinear al mismo contrato |
| pdf-voice-ai | `pdf_voice_ai` | job PDF / voz | Gateway si usa LLM |

---

## 7. Multi-sitio del gateway y KPIs

LiteLLM corre en **local · AWS · réplica (GCP/Oracle)** ([llm-gateway](https://github.com/tfan80921-cell/llm-gateway)).

- Cada sitio tiene su spend; en Grafana usar label `site=local|aws|replica` si se exporta.  
- Las apps de prod apuntan a AWS; fallback a réplica es fase HA.  
- Dev local no debe mezclarse en paneles de prod (filtrar por `site` o datasource).

---

## 8. Plan de adopción (esta semana / piloto)

1. **No** trackear 20 series: solo los 3 del MVP.  
2. Un solo flujo: p. ej. chat Cotorr (o el agente WhatsApp cuando exista).  
3. Variable Grafana `project` / `agent_id`.  
4. LiteLLM local arriba (`chat-free`) antes de obsesionarse con costo real.  
5. Documentar en cada repo un enlace a **este** framework.

Checklist:

- [ ] Evento JSON al cierre del path crítico  
- [ ] `/metrics` o spend LiteLLM scrapeable  
- [ ] Alloy → Grafana Cloud  
- [ ] 3 paneles MVP  
- [ ] Sin `client_id` en labels Prometheus  

---

## 9. Corroboración con el texto de referencia

| Idea del texto original | Estado en el ecosistema |
|-------------------------|-------------------------|
| 4 pilares costo / uso / negocio / calidad | Adoptados como contrato (§3) |
| Un evento por chat | `kpi_chat` + extensión `project`/`service` |
| Prometheus + Loki vía Alloy | Objetivo; Cotorr ya emite métricas y log JSON |
| Empezar con 3 KPIs | Obligatorio en piloto (§8) |
| Costo por proveedor | LiteLLM cascada multi-proveedor |
| ROI vs humano | Panel Grafana, no lógica en cada agente |

---

## 10. Referencias rápidas

- Cotorr metrics: `GET /metrics` · `docs/KPI.md`  
- Gateway: https://github.com/tfan80921-cell/llm-gateway  
- Prometheus naming corto: `docs/KPI_PROMETHEUS_GRAFANA.md`  

---

*Documento vivo. Cualquier producto nuevo del ecosistema debe enlazar este framework antes de inventar nombres de métricas propios.*
