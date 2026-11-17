# UTN-METODOLOGIA-TPI — Agenda de turnos para consultorio odontológico

TPI de **Metodología I** (UTN) · Comisión 3 · Trabajo individual de **Ignacio Martín Rodríguez**.

Sistema para que el personal de un consultorio odontológico **ficticio** registre turnos sin dobles reservas y vea la agenda del día. Se desarrolló con un agente de IA siguiendo **Discovery → Base de conocimiento → Roadmap → changes OpenSpec con TDD**.

> Todos los datos son ficticios. No hay pacientes, credenciales ni servicios externos reales.

## Qué hace

| Change | Funcionalidad | Stack que incorpora | Estado |
| --- | --- | --- | --- |
| **C-01** `registrar-turno-sin-solapamientos` | `POST /turnos`: registra un turno y rechaza si el profesional o el box ya están ocupados | Python, FastAPI, SQLAlchemy | ✅ Archivado |
| **C-02** `consultar-agenda-diaria` | `GET /agenda` + pantalla React "Agenda del día" con filtros | React, TypeScript, Vite | ✅ Archivado |
| **C-03** `autenticar-personal-jwt` | Login con JWT, permisos por rol y cierre de sesión con Redis; pantalla de ingreso | JWT, Redis | ✅ Archivado |
| **C-04** `persistencia-postgresql-y-docker` | PostgreSQL sin dobles reservas simultáneas y todo el sistema con Docker Compose | PostgreSQL, Docker | ✅ Archivado |

Plan completo (C-05 a C-08) en [ROADMAP.md](ROADMAP.md).

## Stack

Python 3.12+ · FastAPI · **JWT** · SQLAlchemy · **PostgreSQL** · **Redis** · **Docker / Docker Compose** · React · TypeScript · Vite · OpenSpec

SQLite queda como base por defecto para desarrollar sin instalar nada; PostgreSQL y Redis se usan con Docker Compose.

## Estructura

```text
├── AGENTS.md / CLAUDE.md      Instrucciones para el agente (idénticos)
├── ROADMAP.md                 Changes C-01 a C-08, fases y dependencias
├── docker-compose.yml         PostgreSQL + Redis + backend + frontend
├── .env.example               Variables a completar en .env (no se sube)
├── discovery/                 Problema, actores, referencias y alcance
├── knowledge-base/            Visión, roles y permisos, datos, reglas, funcionalidades, arquitectura, decisiones
├── openspec/
│   ├── specs/                 registro-turnos, agenda-diaria, autenticacion-personal, persistencia-postgresql-docker
│   └── changes/archive/       C-01 a C-04 con proposal, design, specs y tasks
├── backend/
│   ├── odontologia/           api.py · servicio.py · autenticacion.py · db.py · errores.py · datos_demo.py
│   ├── tests/                 62 pruebas (unittest)
│   └── Dockerfile
├── frontend/                  React + TS + Vite: Ingreso y Agenda del día (17 pruebas), Dockerfile y nginx.conf
├── .agents/skills/            Skill propia: odontologia-turnos
├── .atl/skill-registry.md     Skills usadas y en qué etapa
├── docs/
│   ├── BITACORA.md            Cómo se construyó, auditoría y limitaciones
│   ├── evidencia/             RED/GREEN y resultados de cada change
│   └── skills-mcp/            Skill propia y MCP Context7
└── scripts/verificar.ps1      Verifica todo en Windows
```

## Usuarios de demostración (ficticios)

| Usuario | Rol | Puede registrar turnos | Puede ver la agenda |
| --- | --- | --- | --- |
| `recepcion` | Recepción | ✅ | ✅ |
| `profesional` | Profesional | ❌ (403) | ✅ |
| `admin` | Administración | ✅ | ✅ |

Clave de los tres: **`Clave-Demo-2026`**. Es ficticia y pública a propósito; en la base sólo se guarda su hash.

## Opción A — Sin Docker (desarrollo)

Requisitos: Python 3.12+ y Node.js 20+.

```bash
# 1) Backend
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn odontologia.api:crear_app --factory --reload
```

- API: http://127.0.0.1:8000 · Swagger: http://127.0.0.1:8000/docs
- Usa SQLite (`odontologia.db`, se crea sola) y sesiones cerradas en memoria.
- Sin `ODONTOLOGIA_JWT_SECRETO` se genera un secreto temporal (aparece una advertencia y las sesiones se pierden al reiniciar).

```bash
# 2) Frontend (con el backend corriendo)
cd frontend
npm install
npm run dev
```

Abrir http://localhost:5173 e ingresar con un usuario de la tabla.

## Opción B — Con Docker Compose (stack completo)

Requisito: Docker Desktop.

```bash
cp .env.example .env        # Windows: copy .env.example .env
# Completar en .env: POSTGRES_PASSWORD y ODONTOLOGIA_JWT_SECRETO (≥ 32 caracteres)
#   python -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose up --build
```

- Pantalla: http://localhost:8080 · API/Swagger: http://localhost:8000/docs
- Levanta PostgreSQL 16, Redis 7, backend y frontend (Nginx).
- Para borrar los datos: `docker compose down -v`.

## Pruebas

```bash
# Backend: 62 pruebas (C-01 a C-04) con SQLite
cd backend
python -m unittest discover -s tests -t . -v

# Las mismas pruebas contra PostgreSQL y Redis reales (bases descartables)
ODONTOLOGIA_TEST_DB_URL=postgresql+psycopg://usuario:clave@127.0.0.1:5432/odontologia_test \
ODONTOLOGIA_TEST_REDIS_URL=redis://127.0.0.1:6379/15 \
python -m unittest discover -s tests -t .

# Frontend: 17 pruebas + compilación
cd frontend
npm test
npm run build

# Specs y Docker
openspec list
openspec validate --all --strict
docker compose config -q
```

Sin `ODONTOLOGIA_TEST_REDIS_URL`, las 3 pruebas de Redis se omiten. En Windows, todo junto: `powershell -ExecutionPolicy Bypass -File scripts\verificar.ps1`.

## Demo rápida en Swagger

1. **POST /auth/login** con `{"usuario": "recepcion", "clave": "Clave-Demo-2026"}` → copiar `access_token`.
2. Botón **Authorize** → pegar el token.
3. Probar:

| # | Acción | Resultado esperado |
| --- | --- | --- |
| 1 | `POST /turnos` PAC-001, PRO-001, BOX-1, 09:00–09:30 `-03:00` del 2026-12-01 | **201**, horas en UTC (12:00Z–12:30Z) |
| 2 | Mismo profesional, BOX-2, 09:15–09:45 | **409** `conflicto_profesional` |
| 3 | PRO-002 en BOX-1, 09:10–09:20 | **409** `conflicto_box` |
| 4 | PRO-001, BOX-1, 09:30–10:00 (pegado) | **201** |
| 5 | `inicio` sin zona: `2026-12-01T09:00:00` | **422** `entrada_invalida` |
| 6 | Sin token (Logout del Authorize) | **401** `no_autenticado` |
| 7 | Login como `profesional` y `POST /turnos` | **403** `sin_permiso` |
| 8 | `GET /agenda?fecha=2026-12-01` | **200** con los turnos ordenados |
| 9 | `POST /auth/logout` y reintentar con el mismo token | **204** y luego **401** `token_invalido` |

## Reglas principales

- Un turno ocupa `[inicio, fin)`: turnos pegados se permiten.
- Un profesional y un box no pueden tener turnos superpuestos (si chocan ambos, se informa el profesional).
- Fechas con zona horaria, guardadas en UTC; el consultorio está en UTC-03:00.
- Dos altas simultáneas del mismo recurso: sólo una se registra (SQLite: `BEGIN IMMEDIATE`; PostgreSQL: `SELECT … FOR UPDATE`).
- Sólo el personal con sesión usa la agenda; registrar turnos es de Recepción y Administración.

Detalle en [knowledge-base/04_reglas_de_negocio.md](knowledge-base/04_reglas_de_negocio.md) y [02_actores_y_roles.md](knowledge-base/02_actores_y_roles.md).

## Metodología, skill y MCP

- **Flujo:** Active Stack (fundación) + OpenSpec (explore → propose → apply → verify → archive). Ver [AGENTS.md](AGENTS.md).
- **Skill propia:** [`odontologia-turnos`](.agents/skills/odontologia-turnos/SKILL.md), creada con la guía de `skill-creator`. Necesidad, adaptación e integración en [docs/skills-mcp/skill-propia.md](docs/skills-mcp/skill-propia.md).
- **MCP:** Context7, para consultar documentación actualizada de Vite en C-02. Ver [docs/skills-mcp/mcp-context7.md](docs/skills-mcp/mcp-context7.md).

## Uso de IA

El código y la documentación se generaron con asistencia de un agente de IA (Claude) bajo indicaciones del alumno. Las pruebas en `docs/evidencia/` indican quién las ejecutó y dónde; las limitaciones están en [docs/BITACORA.md](docs/BITACORA.md).
