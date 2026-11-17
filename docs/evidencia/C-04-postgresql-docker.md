# Evidencia — C-04 persistencia-postgresql-y-docker

Pruebas ejecutadas por el agente de IA (Claude) el 2026-11-16 contra **PostgreSQL 16.15** y **Redis 7.0.15** reales en Linux, con psycopg 3.2.9 y SQLAlchemy 2.0.40. **No son una verificación del alumno.**

## RED: la carrera existe en PostgreSQL

Con la suite apuntando a PostgreSQL y **sin** `FOR UPDATE`:

```text
$ ODONTOLOGIA_TEST_DB_URL=postgresql+psycopg://…/odontologia_test python -m unittest tests.test_registro_turnos.Concurrencia
AssertionError: Lists differ: ['ok', 'ok'] != ['conflicto_profesional', 'ok']   (5 de 5 rondas)
AssertionError: Lists differ: ['ok', 'ok'] != ['conflicto_box', 'ok']           (4 de 5 rondas)
AssertionError: 10 != 5  /  9 != 5   (turnos duplicados en la base)
FAILED (failures=11)
```

La misma prueba en SQLite pasaba (`BEGIN IMMEDIATE` de C-01).

## GREEN

Con `SELECT … FOR UPDATE` (profesional → box):

```text
# Concurrencia en PostgreSQL, tres corridas seguidas
OK
OK
OK

# Suite completa contra PostgreSQL + Redis, tres corridas seguidas
Ran 62 tests ... OK
Ran 62 tests ... OK
Ran 62 tests ... OK

# Suite completa en SQLite (por defecto)
Ran 62 tests ... OK (skipped=3 sin Redis)
```

## Docker

```text
$ POSTGRES_PASSWORD=x ODONTOLOGIA_JWT_SECRETO=y docker compose config -q
(sin errores)

$ POSTGRES_PASSWORD= docker compose config -q
required variable POSTGRES_PASSWORD is missing a value: Definir POSTGRES_PASSWORD en .env
```

**Limitación:** en el entorno del agente Docker Hub no es accesible (`Forbidden` al bajar imágenes), así que **no** se construyeron ni levantaron los contenedores. Se verifica en la PC del alumno con `docker compose up --build` (ver README).

## Prueba manual sobre PostgreSQL

Uvicorn con `ODONTOLOGIA_DB_URL=postgresql+psycopg://…` y `ODONTOLOGIA_REDIS_URL`: login 200, alta 201, agenda 200, logout 204, token revocado 401. `select count(*) from turnos` → 1.

## Cobertura de la spec `persistencia-postgresql-docker`

| Requirement | Evidencia |
| --- | --- |
| Base configurable | Suite completa (62) contra PostgreSQL |
| Altas simultáneas en PostgreSQL | `Concurrencia.test_dos_altas_simultaneas_del_mismo_profesional` y `..._del_mismo_box` (5 rondas cada una) |
| Stack con Docker Compose | `docker compose config` |
| Secretos fuera del repo | `.env.example` vacío, `.env` en `.gitignore`, error si falta la variable |

## Revisión con la skill `odontologia-turnos`

| # | Invariante | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Intervalo `[inicio, fin)` | ✅ | Misma consulta en ambas bases |
| 2 | Zona horaria / UTC | ✅ | `TIMESTAMP` sin zona con valores UTC, igual que SQLite |
| 3 | No solapamiento | ✅ | Verificación e INSERT en la misma transacción |
| 4 | Concurrencia | ✅ | Mecanismo propio de PostgreSQL documentado y probado con conexiones independientes (RED → GREEN) |
| 5 | Errores | ✅ | Sin códigos nuevos |
| 6 | Capas | ✅ | El bloqueo vive en `servicio.py` |
| 7 | Datos ficticios / secretos | ✅ | Secretos sólo en `.env` |
| 8 | Pruebas | ✅ | Suite completa en ambas bases |
| 9 | Alcance | ✅ | Sin Alembic ni despliegue público |
| 10 | Seguridad | ✅ | Puertos sólo en `127.0.0.1`; backend sin root en Docker |

**Bloqueantes:** ninguno.
