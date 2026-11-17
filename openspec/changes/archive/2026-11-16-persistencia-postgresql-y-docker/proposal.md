# Proposal — C-04 persistencia-postgresql-y-docker

## Why

La cátedra fijó **PostgreSQL** y **Docker / Docker Compose** como parte del stack. Además, la garantía de C-01 (`BEGIN IMMEDIATE`) sólo vale para SQLite en un equipo: con PostgreSQL dos altas simultáneas **sí** se registraban ambas (comprobado: 9 de 10 rondas fallaron en la prueba de concurrencia).

## What Changes

- Soporte de PostgreSQL por `ODONTOLOGIA_DB_URL` con el driver `psycopg` 3.
- Bloqueo `SELECT … FOR UPDATE` de la fila del profesional y luego del box al registrar un turno.
- La suite completa puede correr contra PostgreSQL con `ODONTOLOGIA_TEST_DB_URL`.
- Pruebas de concurrencia más fuertes: cinco rondas por profesional y cinco por box.
- `Dockerfile` del backend y del frontend (Vite compilado + Nginx con proxy `/api`).
- `docker-compose.yml` con `db` (PostgreSQL 16), `redis` (Redis 7), `backend` y `frontend`, con healthchecks.
- `.env.example` sin valores; los secretos van en `.env` (ignorado por Git).

## Capabilities

### New Capabilities

- `persistencia-postgresql-docker`: PostgreSQL con la misma garantía de no solapamiento y stack completo con Docker Compose.

### Modified Capabilities

- `registro-turnos`: el requisito de altas simultáneas incluye el bloqueo de filas en PostgreSQL y el caso del box.

## Fuera de alcance

Migraciones con Alembic (el esquema se crea con `create_all`), despliegue público, HTTPS, réplicas y backups.

## Impact

- Backend: `servicio.registrar_turno` bloquea filas; `db.crear_motor` con `pool_pre_ping` para PostgreSQL.
- Dependencia nueva: `psycopg[binary]`.
- Archivos nuevos: `docker-compose.yml`, `.env.example`, `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `frontend/package-lock.json`.
- SQLite sigue siendo la opción por defecto para desarrollo sin Docker.
