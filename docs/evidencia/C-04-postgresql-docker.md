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

## Verificación con Docker en la PC del alumno (2026-11-18)

Windows con Docker Desktop recién instalado, ejecutado por el agente con control de la PC del alumno. `.env` generado localmente (no versionado).

```text
$ docker compose up --build -d
 Image utn-metodologia-tpi-frontend Built
 Image utn-metodologia-tpi-backend Built
 Container utn-metodologia-tpi-db-1 Healthy
 Container utn-metodologia-tpi-redis-1 Healthy
 Container utn-metodologia-tpi-backend-1 Started
 Container utn-metodologia-tpi-frontend-1 Started

$ docker compose ps
backend    Up   127.0.0.1:8000->8000/tcp
db         Up (healthy)
frontend   Up   127.0.0.1:8080->80/tcp
redis      Up (healthy)

GET http://127.0.0.1:8000/health  → {"estado":"ok"}
GET http://127.0.0.1:8080/        → 200
```

Pedidos reales a través del frontend en Docker (`http://localhost:8080/api/...`, Nginx → backend → PostgreSQL / Redis):

| Pedido | Resultado |
| --- | --- |
| `POST /turnos` sin token | 401 `no_autenticado` |
| Login `recepcion` + `POST /turnos` 09:00–09:30 | 201 (`12:00Z`–`12:30Z`) |
| Mismo profesional, BOX-2, 09:15–09:45 | 409 `conflicto_profesional` |
| Turno pegado 09:30–10:00 | 201 |
| `inicio` sin zona horaria | 422 `entrada_invalida` |
| Login `profesional` + `POST /turnos` | 403 `sin_permiso` |
| `GET /agenda?fecha=2026-12-01` | 200 con los 2 turnos |
| `POST /auth/logout` y reintento con el mismo token | 204 y luego 401 `token_invalido` |

Pantalla en `http://localhost:8080`: ingreso como `recepcion`, fecha 01/12/2026 → tabla con 09:00 – 09:30 y 09:30 – 10:00.

Datos guardados, consultados dentro de los contenedores:

```text
PostgreSQL  select … from turnos   → 2 filas (PRO-001, BOX-1, 12:00–12:30 y 12:30–13:00 UTC)
PostgreSQL  select … from usuarios → recepcion, profesional, admin con hash pbkdf2_sha256$… (sin claves)
Redis       --scan odontologia:revocado:* → odontologia:revocado:82c2a3cb57d34ffb8bfd8997b77d3d14
```

Con esto queda resuelta la limitación anterior: Docker Compose se construyó, levantó y usó de punta a punta.
