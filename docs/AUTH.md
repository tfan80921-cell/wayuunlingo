# Wayuunlingo — Autenticación (Google + Better Auth)

**Estado:** Documentación de diseño (alineada a cotorr)  
**Fecha:** 2026-10-17  
**Regla general del ecosistema:** login con **Google OAuth** vía **Better Auth** (u equivalente estable ya usado en otros repos).

---

## 1. Propósito

Cuando exista app o API multiusuario, autenticar de forma segura a:

- Administradores / equipo ML (runs, corpus, métricas)  
- Revisores EIB (evaluación humana, feedback cultural)  
- Usuarios finales (traducción texto/voz)

El **pipeline de fine-tuning por scripts no requiere Auth**. Auth entra en la capa producto/API.

---

## 2. Stack de referencia (cotorr)

| Variable | Uso |
|----------|-----|
| `BETTER_AUTH_SECRET` | Secreto de sesión (≥ 32 chars; `openssl rand -hex 32`) |
| `BETTER_AUTH_URL` | URL pública del servidor de auth/API |
| `GOOGLE_CLIENT_ID` | OAuth client (Google Cloud) |
| `GOOGLE_CLIENT_SECRET` | OAuth secret |
| `DATABASE_URL` | Neon: tablas de sesión/usuario de Better Auth |

Flujo típico:

1. Configurar OAuth Web client en Google Cloud.  
2. Redirect autorizado: `{BETTER_AUTH_URL}/api/auth/callback/google`  
3. Provisionar tablas:  
   `pnpm dlx auth@... migrate --config src/auth/auth.ts` (o el path del proyecto)  
4. Endpoints bajo `/api/auth/*` gestionados por Better Auth.

---

## 3. Roles previstos (RBAC simple)

| Rol | Capacidades |
|-----|-------------|
| `admin` | Todo: corpus, lanzar/ver runs, config, usuarios |
| `reviewer_eib` | Ver pares, anotar adecuación/fluidez/cultural, marcar dudosos |
| `user` | Traducir (texto/voz), historial propio si se persiste |

Implementación mínima: columna `role` en tabla de usuario (o claims en sesión). Sin roles complejos al inicio.

---

## 4. Qué protege Auth (y qué no)

| Recurso | ¿Auth? |
|---------|--------|
| Scripts locales `process` / `train` / `evaluate` | No |
| `evaluation_history.json` en disco de CI/GPU | No (secretos de máquina) |
| API de traducción en producción | Sí (o rate-limit + API key de servicio) |
| Dashboard interno de KPIs con datos sensibles | Sí |
| Endpoints de escritura a Neon (pares, runs) | Sí |
| STT/TTS proxy (coste API) | Sí o clave de servicio + cuota |

**Lección de cotorr:** no usar solo `installationId` en localStorage como “auth”; eso no es frontera de seguridad.

---

## 5. Integración con Neon

- Better Auth usa Postgres (Neon) para usuarios, sesiones, cuentas OAuth.  
- Tablas de dominio Wayuunlingo (`translation_pairs`, `training_runs`, …) quedan **aparte**, con `user_id` opcional donde aplique (p. ej. feedback EIB, historial de traducciones).

---

## 6. Variables de entorno (checklist)

```bash
DATABASE_URL=
BETTER_AUTH_SECRET=
BETTER_AUTH_URL=http://localhost:3000   # o URL de producción
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

Nunca commitear `.env`. En Vercel/hosting: secretos del proyecto.

---

## 7. Criterios de aceptación

- [ ] Documento de roles y variables acordado.  
- [ ] OAuth Google configurado solo cuando exista front/API.  
- [ ] Pipeline offline sigue sin dependencia de Auth.  
- [ ] Ningún endpoint costoso (LLM/STT/TTS) queda abierto sin control en producción.

---

## 8. Referencias

- `cotorr`: `.env.example`, Better Auth + Google, `docs/ARCHITECTURE.md`  
- Wayuunlingo: `docs/NEON.md`, `docs/FINE_TUNING_PIPELINE.md`
