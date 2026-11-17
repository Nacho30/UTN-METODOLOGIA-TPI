# Design — C-04 persistencia-postgresql-y-docker

## Context

C-01 serializa altas con `BEGIN IMMEDIATE`, que es propio de SQLite. En PostgreSQL, con aislamiento READ COMMITTED, dos transacciones pueden consultar a la vez, ver el horario libre e insertar ambas.

## Goals / Non-Goals

**Goals:** misma garantía en PostgreSQL, stack completo de la cátedra en Docker Compose, cero secretos en el repo.

**Non-Goals:** migraciones versionadas, alta disponibilidad, despliegue en la nube.

## Decisions

### D1 — Bloqueo de filas del recurso con `FOR UPDATE`
Antes de buscar solapamientos se ejecuta `SELECT id FROM profesionales WHERE id = … FOR UPDATE` y lo mismo para `boxes`. La segunda transacción que pide el mismo recurso espera al COMMIT de la primera y, como READ COMMITTED toma una foto nueva en cada sentencia, después **ve** el turno recién insertado y devuelve conflicto.
*Alternativas descartadas:* `SERIALIZABLE` (obliga a reintentar ante errores de serialización); restricción `EXCLUDE` con `tstzrange` (sólo PostgreSQL y no da el error por recurso en el orden pedido).

### D2 — Orden fijo profesional → box
Toda alta bloquea primero un profesional y después un box. Nunca una transacción tiene un box y espera un profesional, así que no se forman ciclos (deadlock).

### D3 — Mismo código para SQLite y PostgreSQL
SQLAlchemy no emite `FOR UPDATE` en SQLite; ahí sigue protegiendo `BEGIN IMMEDIATE`. Las reglas no cambian según la base.

### D4 — La suite completa contra PostgreSQL
`tests/apoyo.py` lee `ODONTOLOGIA_TEST_DB_URL`; si está definida, cada prueba crea y borra el esquema en esa base. Así las 62 pruebas validan PostgreSQL sin duplicarlas.

### D5 — Docker Compose
- `db`: `postgres:16-alpine` con volumen y `pg_isready`.
- `redis`: `redis:7-alpine` con `redis-cli ping`. Lo usa C-03 para las sesiones cerradas.
- `backend`: Python 3.12 slim, usuario sin privilegios, espera a `db` y `redis` sanos.
- `frontend`: compila con `npm ci` + `vite build` y sirve con Nginx, que reenvía `/api/` al backend (igual que el proxy de Vite).
- Puertos sólo en `127.0.0.1`. Variables obligatorias con `${VAR:?mensaje}`.

### D6 — psycopg 3
Driver oficial moderno de PostgreSQL, soportado por SQLAlchemy 2 (`postgresql+psycopg`), con ruedas binarias para Windows.

## Risks / Trade-offs

- **Sin Alembic:** un cambio de esquema futuro necesitará migraciones → change propio.
- **Docker no se pudo ejecutar en el entorno del agente** (sin acceso a Docker Hub): se validó la sintaxis con `docker compose config`; levantar los contenedores queda para la PC del alumno.
