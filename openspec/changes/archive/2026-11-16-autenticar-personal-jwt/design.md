# Design — C-03 autenticar-personal-jwt

## Context

La API de C-01/C-02 no tenía identidad. La cátedra exige JWT y Redis. La matriz de permisos era la pregunta abierta Q04.

## Goals / Non-Goals

**Goals:** login con JWT, permisos por rol aplicados en el backend, cierre de sesión real, sin secretos en el repo.

**Non-Goals:** gestión de usuarios, refresh tokens, SSO.

## Decisions

### D1 — JWT HS256 de 30 minutos con `jti`
Token firmado con un secreto simétrico (`ODONTOLOGIA_JWT_SECRETO`, mínimo 32 caracteres). `jwt.decode` exige `sub`, `rol`, `jti` y `exp`, y acepta **sólo** HS256: así se rechazan tokens con `alg: none`. Sin secreto configurado se genera uno temporal con advertencia (útil en desarrollo; las sesiones se pierden al reiniciar).

### D2 — Cerrar sesión con Redis
Un JWT no se puede "borrar": es válido hasta `exp`. Para cerrar sesión se guarda su `jti` en Redis (`odontologia:revocado:<jti>`) con TTL igual a lo que le queda al token, así Redis lo borra solo. Sin `ODONTOLOGIA_REDIS_URL` se usa una lista en memoria con la misma interfaz (`revocar`, `esta_revocado`); en Docker Compose (C-04) se usa Redis.
*Alternativa descartada:* tokens cortos sin logout — no cumple el uso de Redis del stack ni permite cerrar sesión.

### D3 — PBKDF2-SHA256 de la biblioteca estándar
260.000 iteraciones, sal de 16 bytes y comparación en tiempo constante (`hmac.compare_digest`). No agrega dependencias.

### D3b — Clave de demostración fuera del repositorio (corrección de auditoría)
La primera versión de C-03 dejaba la clave de demostración escrita en el código y en el README. La consigna del TPI pide mantener "claves, tokens y contraseñas fuera del repositorio, de la entrega y del video", así que en la auditoría del 2026-11-16 se corrigió: la clave se lee de `ODONTOLOGIA_CLAVE_DEMO` (variable de entorno o `.env`), se guarda sólo su hash y, si falta, no se crean usuarios. Las pruebas generan una clave al azar en cada corrida. El cambio quedó en un commit propio para conservar la trazabilidad.

### D4 — Matriz de permisos (resuelve Q04)

| Operación | recepcion | profesional | administracion |
| --- | --- | --- | --- |
| Registrar turno | ✅ | ❌ | ✅ |
| Consultar agenda / catálogo | ✅ | ✅ | ✅ |

Vive en `autenticacion.PERMISOS` (backend). El permiso se evalúa como dependencia de FastAPI, **antes** de leer el cuerpo: un profesional recibe 403 aunque mande datos inválidos.

### D5 — Mismo error para usuario inexistente y clave incorrecta
Ambos responden 401 `credenciales_invalidas` con el mismo mensaje, para no revelar qué usuarios existen.

### D6 — Frontend: `sessionStorage` y vuelta al login ante 401
La sesión se guarda en `sessionStorage` (se borra al cerrar la pestaña), con `try/catch` por si el navegador bloquea el almacenamiento. Cualquier 401 devuelve al ingreso con aviso. Los permisos **no** se deciden en el frontend.

## Risks / Trade-offs

- **Revocación en memoria** no se comparte entre procesos → en Docker se usa Redis.
- **Token en `sessionStorage`** es accesible por JavaScript de la página; aceptable para una demo local sin contenido de terceros.
- **Sin límite de intentos de login** → queda para un change futuro.
