# UTN-METODOLOGIA-TPI — Agenda de turnos para consultorio odontológico

TPI de **Metodología I** (UTN) · Comisión 3 · Trabajo individual de **Ignacio Martín Rodríguez**.

Sistema para que Recepción de un consultorio odontológico **ficticio** registre turnos sin dobles reservas y vea la agenda del día. Se desarrolló con un agente de IA siguiendo **Discovery → Base de conocimiento → Roadmap → changes OpenSpec con TDD**.

> Todos los datos son ficticios. No hay pacientes, credenciales ni servicios externos reales.

## Qué hace

| Change | Funcionalidad | Estado |
| --- | --- | --- |
| **C-01** `registrar-turno-sin-solapamientos` | `POST /turnos`: registra un turno y rechaza si el profesional o el box ya están ocupados | ✅ Archivado |
| **C-02** `consultar-agenda-diaria` | `GET /agenda` + pantalla React "Agenda del día" con filtros | ✅ Archivado |

El plan completo (C-03 a C-08) está en [ROADMAP.md](ROADMAP.md).

## Stack

Python 3.12+ · FastAPI · SQLAlchemy · SQLite · React · TypeScript · Vite · OpenSpec

## Estructura

```text
├── AGENTS.md / CLAUDE.md      Instrucciones para el agente (idénticos)
├── ROADMAP.md                 Changes C-01 a C-08, fases y dependencias
├── discovery/                 Problema, actores, referencias y alcance
├── knowledge-base/            Visión, actores, datos, reglas, funcionalidades, arquitectura, decisiones
├── openspec/
│   ├── specs/                 Specs vigentes: registro-turnos, agenda-diaria
│   └── changes/archive/       C-01 y C-02 con proposal, design, spec y tasks
├── backend/
│   ├── odontologia/           api.py · servicio.py (reglas) · db.py · errores.py · datos_demo.py
│   └── tests/                 38 pruebas (unittest)
├── frontend/                  React + TS + Vite (pantalla Agenda del día) y 10 pruebas
├── .agents/skills/            Skill propia: odontologia-turnos
├── .atl/skill-registry.md     Skills usadas y en qué etapa
├── docs/
│   ├── BITACORA.md            Cómo se construyó y limitaciones
│   ├── evidencia/             RED/GREEN y resultados de cada change
│   └── skills-mcp/            Skill propia y MCP Context7
└── scripts/verificar.ps1      Verifica todo en Windows
```

## Requisitos

- Python 3.12 o superior
- Node.js 20 o superior (incluye npm)
- Opcional: OpenSpec CLI (`npm install -g @fission-ai/openspec`)

## Cómo levantarlo

### 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
uvicorn odontologia.api:crear_app --factory --reload
```

- API: http://127.0.0.1:8000
- Swagger (para probar a mano): http://127.0.0.1:8000/docs
- La base `odontologia.db` se crea sola con el catálogo ficticio. Para empezar de cero, borrarla con el servidor detenido.

### 2. Frontend (con el backend corriendo)

```bash
cd frontend
npm install
npm run dev
```

Abrir http://localhost:5173. Vite reenvía `/api/*` al backend.

## Pruebas

```bash
# Backend: 38 pruebas (C-01 y C-02)
cd backend
python -m unittest discover -s tests -t . -v

# Frontend: 10 pruebas de la lógica de la pantalla + compilación
cd frontend
npm test
npm run build

# Specs
openspec list
openspec validate --all --strict
```

En Windows, todo junto: `powershell -ExecutionPolicy Bypass -File scripts\verificar.ps1`

## Demo rápida (Swagger o curl)

Datos ficticios disponibles: pacientes `PAC-001`, `PAC-002`; profesionales `PRO-001`, `PRO-002`; boxes `BOX-1`, `BOX-2`.

| # | Acción | Resultado esperado |
| --- | --- | --- |
| 1 | `POST /turnos` PAC-001, PRO-001, BOX-1, 09:00–09:30 `-03:00` del 2026-12-01 | **201**, horas en UTC (12:00Z–12:30Z) |
| 2 | Mismo profesional, BOX-2, 09:15–09:45 | **409** `conflicto_profesional` |
| 3 | PRO-002 en BOX-1, 09:10–09:20 | **409** `conflicto_box` |
| 4 | PRO-001, BOX-1, 09:30–10:00 (pegado) | **201** |
| 5 | `inicio` sin zona: `2026-12-01T09:00:00` | **422** `entrada_invalida` |
| 6 | `box_id`: `BOX-9` | **404** `recurso_desconocido` |
| 7 | `GET /agenda?fecha=2026-12-01` | **200** con los turnos ordenados |
| 8 | Pantalla web en la fecha 01/12/2026 | Tabla con horarios 09:00 – 09:30 y 09:30 – 10:00 |

Ejemplo de cuerpo:

```json
{
  "paciente_id": "PAC-001",
  "profesional_id": "PRO-001",
  "box_id": "BOX-1",
  "inicio": "2026-12-01T09:00:00-03:00",
  "fin": "2026-12-01T09:30:00-03:00"
}
```

## Reglas principales

- Un turno ocupa `[inicio, fin)`: turnos pegados se permiten.
- Un profesional y un box no pueden tener turnos superpuestos (si chocan ambos, se informa el profesional).
- Las fechas llevan zona horaria y se guardan en UTC; el consultorio está en UTC-03:00.
- Dos altas simultáneas para el mismo recurso: sólo una se registra (`BEGIN IMMEDIATE`).

Detalle en [knowledge-base/04_reglas_de_negocio.md](knowledge-base/04_reglas_de_negocio.md).

## Metodología, skill y MCP

- **Flujo:** Active Stack (fundación) + OpenSpec (explore → propose → apply → verify → archive). Ver [AGENTS.md](AGENTS.md).
- **Skill propia:** [`odontologia-turnos`](.agents/skills/odontologia-turnos/SKILL.md), creada con la guía de `skill-creator`. Necesidad, adaptación e integración en [docs/skills-mcp/skill-propia.md](docs/skills-mcp/skill-propia.md).
- **MCP:** Context7, para consultar documentación actualizada de Vite en C-02. Ver [docs/skills-mcp/mcp-context7.md](docs/skills-mcp/mcp-context7.md).

## Uso de IA

El código y la documentación se generaron con asistencia de un agente de IA (Claude) bajo indicaciones del alumno. Las pruebas que figuran en `docs/evidencia/` las ejecutó el agente; las limitaciones están en [docs/BITACORA.md](docs/BITACORA.md).
