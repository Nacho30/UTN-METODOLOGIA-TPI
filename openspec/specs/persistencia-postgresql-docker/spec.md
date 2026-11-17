# persistencia-postgresql-docker Specification

## Purpose
Ejecutar el sistema sobre PostgreSQL manteniendo la garantía de no solapamiento ante altas simultáneas, y levantar el stack completo (PostgreSQL, Redis, backend y frontend) con Docker Compose. Origen: change C-04 `persistencia-postgresql-y-docker`.

## Requirements

### Requirement: Base configurable
El sistema SHALL usar la base indicada en `ODONTOLOGIA_DB_URL`: SQLite por defecto y PostgreSQL con `postgresql+psycopg://…`. Las mismas reglas, códigos de error y respuestas SHALL valer para ambas bases.

#### Scenario: Suite completa en PostgreSQL
- **GIVEN** `ODONTOLOGIA_TEST_DB_URL` apunta a una base PostgreSQL vacía
- **WHEN** se ejecuta la suite completa del backend
- **THEN** todas las pruebas pasan igual que con SQLite

### Requirement: Altas simultáneas serializadas en PostgreSQL
Al registrar un turno, el sistema SHALL bloquear con `SELECT … FOR UPDATE` la fila del profesional y luego la del box, dentro de la misma transacción que verifica solapamientos e inserta. El orden fijo profesional → box MUST evitar bloqueos mutuos.

#### Scenario: Mismo profesional al mismo tiempo
- **GIVEN** PostgreSQL
- **WHEN** dos conexiones registran a la vez el mismo profesional en el mismo horario, en cinco días distintos
- **THEN** en cada día hay un alta y un `conflicto_profesional`

#### Scenario: Mismo box al mismo tiempo
- **GIVEN** PostgreSQL
- **WHEN** dos conexiones registran a la vez el mismo box con distintos profesionales, en cinco días distintos
- **THEN** en cada día hay un alta y un `conflicto_box`

### Requirement: Stack completo con Docker Compose
`docker-compose.yml` SHALL definir los servicios `db` (PostgreSQL 16), `redis` (Redis 7), `backend` (FastAPI) y `frontend` (Vite compilado servido por Nginx, con `/api` reenviado al backend). El backend SHALL esperar a que `db` y `redis` estén sanos. Los puertos SHALL publicarse sólo en `127.0.0.1`.

#### Scenario: Configuración válida
- **WHEN** se ejecuta `docker compose config` con las variables definidas
- **THEN** la configuración es válida

### Requirement: Secretos fuera del repositorio
La clave de PostgreSQL y el secreto JWT SHALL leerse de un archivo `.env` ignorado por Git; el repositorio SHALL incluir sólo `.env.example` sin valores. Si faltan, Docker Compose MUST negarse a iniciar con un mensaje claro.

#### Scenario: Falta la clave de la base
- **WHEN** se ejecuta `docker compose config` sin `POSTGRES_PASSWORD`
- **THEN** falla con "Definir POSTGRES_PASSWORD en .env"
