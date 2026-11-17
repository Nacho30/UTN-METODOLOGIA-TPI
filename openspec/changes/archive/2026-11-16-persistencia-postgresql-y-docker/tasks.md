# Tasks — C-04 persistencia-postgresql-y-docker

Cada tarea se marcó sólo después de ejecutar sus pruebas. Evidencia en `docs/evidencia/C-04-postgresql-docker.md`.

## 1. PostgreSQL

- [x] 1.1 `tests/apoyo.py` permite correr la suite contra `ODONTOLOGIA_TEST_DB_URL` (crea y borra el esquema por prueba).
- [x] 1.2 Reforzar la concurrencia: cinco rondas por profesional y cinco por box. RED en PostgreSQL 16: 9 de 10 rondas registraron los dos turnos.
- [x] 1.3 `SELECT … FOR UPDATE` de profesional y luego box en `registrar_turno`; GREEN en tres corridas seguidas en PostgreSQL y en SQLite.
- [x] 1.4 `pool_pre_ping` para PostgreSQL y dependencia `psycopg[binary]`.
- [x] 1.5 Suite completa (62 pruebas, con Redis) en verde contra PostgreSQL 16 real.

## 2. Docker

- [x] 2.1 `backend/Dockerfile` (Python 3.12 slim, usuario sin privilegios) y `.dockerignore`.
- [x] 2.2 `frontend/Dockerfile` (multi-etapa: `npm ci` + `vite build` → Nginx) y `nginx.conf` con proxy `/api/`.
- [x] 2.3 `docker-compose.yml` con `db`, `redis`, `backend`, `frontend`, healthchecks y puertos en `127.0.0.1`.
- [x] 2.4 `.env.example` sin valores; `.env` ignorado. `docker compose config` válido y falla con mensaje claro si falta `POSTGRES_PASSWORD`.
- [x] 2.5 Agregar `frontend/package-lock.json` (generado por `npm install` en la PC del alumno) para que `npm ci` sea reproducible.

## 3. Cierre

- [x] 3.1 Prueba manual con Uvicorn sobre PostgreSQL + Redis: login, alta, agenda, logout y token revocado.
- [x] 3.2 Revisión con la skill `odontologia-turnos`.
- [x] 3.3 Sincronizar specs (`persistencia-postgresql-docker` nueva, `registro-turnos` modificada) y archivar.
