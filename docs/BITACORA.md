# Bitácora

Registro honesto de cómo se construyó el proyecto.

## 2026-11-16 — Inicio del repositorio individual

- El alumno pasa a hacer el TPI **solo** y crea el repo `Nacho30/UTN-METODOLOGIA-TPI` (sólo con README).
- Pide un proyecto ordenado con roadmap y dos changes completos, con el mismo tema (agenda odontológica) **hecho desde cero**.
- El agente de IA (Claude) arma la fundación siguiendo el flujo de Active Stack: Discovery → KB → Roadmap → registro de skills → `AGENTS.md`/`CLAUDE.md`, y una skill de dominio propia.
- Discovery: se revisaron dos referencias públicas (AgendaPro y la ayuda de Dentalink) mediante búsqueda web.

## 2026-11-16 — C-01 `registrar-turno-sin-solapamientos`

- Propose: proposal, design (D1–D6), spec y tasks.
- Apply con TDD: RED (`ModuleNotFoundError`), GREEN con 24 pruebas, prueba de mutación de concurrencia (`BEGIN` vs `BEGIN IMMEDIATE`).
- Archivado en `openspec/changes/archive/2026-11-16-registrar-turno-sin-solapamientos/` y spec sincronizada en `openspec/specs/registro-turnos/`.

## 2026-11-16 — C-02 `consultar-agenda-diaria`

- Propose: proposal, design (D1–D6), spec y tasks.
- Apply con TDD: RED (`ImportError`), GREEN con 38 pruebas de backend y 10 de frontend.
- Revisión con la skill `odontologia-turnos`: sin bloqueantes.
- Archivado en `openspec/changes/archive/2026-11-16-consultar-agenda-diaria/` y spec sincronizada en `openspec/specs/agenda-diaria/`.

## Limitaciones conocidas (para no afirmar de más)

- En el entorno del agente **no había acceso** a PyPI, npm ni a la CLI de OpenSpec. Por eso:
  - las pruebas de backend se corrieron con las librerías obtenidas de sus repositorios oficiales (ver evidencia);
  - la estructura de `openspec/` se escribió siguiendo el formato de OpenSpec; queda verificarla con `openspec validate --all --strict` en la PC del alumno;
  - `npm install`, `npm run build` y la pantalla en el navegador quedan para verificar en la PC del alumno.
- La consulta con el MCP Context7 está **pendiente** (ver `docs/skills-mcp/mcp-context7.md`).
- Nada de esto acredita revisión humana: el alumno debe leer y verificar los artefactos.
