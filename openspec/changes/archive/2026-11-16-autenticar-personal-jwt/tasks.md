# Tasks — C-03 autenticar-personal-jwt

Cada tarea se marcó sólo después de ejecutar sus pruebas. Evidencia en `docs/evidencia/C-03-autenticar-personal.md`.

## 1. Pruebas primero

- [x] 1.1 `tests/apoyo.py` (base de prueba, login de ayuda) y `tests/test_autenticacion.py`; adaptar las pruebas de C-01/C-02 para iniciar sesión. RED: `ModuleNotFoundError: odontologia.autenticacion` e `ImportError: CLAVE_DEMO`.

## 2. Backend

- [x] 2.1 `hashear_clave` / `verificar_clave` con PBKDF2-SHA256 y sal aleatoria; hash mal formado → falso.
- [x] 2.2 Modelo `Usuario` y tres usuarios ficticios sembrados con el hash de la clave de demostración.
- [x] 2.3 `POST /auth/login`: validación del cuerpo (422), mismo 401 para usuario inexistente y clave incorrecta, JWT HS256 con `sub`, `rol`, `jti`, `iat`, `exp`.
- [x] 2.4 Dependencia de sesión: 401 `no_autenticado` / `token_invalido` (basura, otro secreto, vencido, sin `jti`, rol desconocido, `alg: none`) con `WWW-Authenticate: Bearer`.
- [x] 2.5 Matriz `PERMISOS` y 403 `sin_permiso` evaluado antes de leer el cuerpo.
- [x] 2.6 `POST /auth/logout` y `GET /auth/yo`; `RevocacionesMemoria` y `RevocacionesRedis` con TTL.
- [x] 2.7 Secreto desde `ODONTOLOGIA_JWT_SECRETO`, mínimo 32 caracteres; temporal con advertencia si falta.
- [x] 2.8 Pruebas de Redis contra un `redis-server` real (`ODONTOLOGIA_TEST_REDIS_URL`).

## 3. Frontend

- [x] 3.1 `src/sesion.test.ts` en RED (`ERR_MODULE_NOT_FOUND`) y luego `src/sesion.ts`: cabecera Bearer, 401 → login, validación del formulario, nombres de rol y almacenamiento tolerante a fallos.
- [x] 3.2 `App.tsx`: pantalla de ingreso, token en cada pedido, "Salir" con `POST /auth/logout`, vuelta al ingreso ante 401.

## 4. Cierre

- [x] 4.1 Suites completas en verde (backend con y sin Redis, frontend) y `ruff check` limpio.
- [x] 4.2 Prueba manual con Uvicorn + Redis: login, alta, logout y token revocado.
- [x] 4.3 Revisión con la skill `odontologia-turnos` (incluye el nuevo punto de seguridad).
- [x] 4.4 Sincronizar specs (`autenticacion-personal` nueva; `registro-turnos` y `agenda-diaria` modificadas) y archivar.
- [x] 4.5 Corrección de auditoría: clave de demostración fuera del repositorio (`ODONTOLOGIA_CLAVE_DEMO`), pruebas con clave al azar y 3 pruebas nuevas (sin clave, clave corta, sólo hash). Suites en verde: 65 pruebas en SQLite y en PostgreSQL + Redis.
