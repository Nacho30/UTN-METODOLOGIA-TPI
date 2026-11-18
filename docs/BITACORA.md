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

## 2026-11-16 — Verificación en la PC del alumno (Windows)

El alumno clonó el repo y ejecutó `scripts\verificar.ps1` (PowerShell 5.1):

- Backend: `Ran 38 tests ... OK`.
- Frontend: pruebas sin fallas y `tsc --noEmit && vite build` correcto (Vite 6.4.6).
- OpenSpec: `openspec validate --all --strict` → `agenda-diaria` y `registro-turnos`, 2 passed, 0 failed. Sin changes activos.
- Resultado final del script: `TODO OK`.

Esto resuelve las verificaciones de npm, build y OpenSpec que habían quedado pendientes.

## 2026-11-16 — Auditoría contra la consigna y la corrección del Parcial 2

El alumno pidió auditar el repo contra el PDF del TPI y los errores del Parcial 2 (hecho en grupo en otro repo). Hallazgos:

| # | Hallazgo | Gravedad | Acción |
| --- | --- | --- | --- |
| A-01 | **Stack incompleto:** faltaban JWT, PostgreSQL, Redis y Docker/Compose. Es el mismo error que la cátedra corrigió en el Parcial 2 ("respetar el stack tecnológico"). La decisión DD-09 los había dejado afuera. | Crítica | C-03 (JWT + Redis) y C-04 (PostgreSQL + Docker). DD-09 revertida. |
| A-02 | En PostgreSQL la protección de C-01 no alcanzaba: dos altas simultáneas se registraban ambas (9 de 10 rondas). | Crítica | `SELECT … FOR UPDATE` en C-04. |
| A-03 | La API no tenía autenticación: cualquiera podía registrar turnos. | Alta | C-03. |
| A-04 | Faltaba `frontend/package-lock.json`: la instalación no era reproducible. | Media | Agregado en C-04. |
| A-05 | Consulta con el MCP Context7 sin evidencia. | Media | Pendiente del alumno (no se puede hacer desde el entorno del agente). |
| A-06 | Guion, casos de Swagger y accesos directos no contemplaban login ni Docker. | Media | Actualizados en la carpeta del TPI. |

## 2026-11-16 — C-03 `autenticar-personal-jwt`

- RED: `ModuleNotFoundError: odontologia.autenticacion` (backend) y `ERR_MODULE_NOT_FOUND sesion.ts` (frontend).
- GREEN: 62 pruebas de backend (con Redis real) y 17 de frontend.
- Revisión con la skill (se le agregó el punto 10, Seguridad): sin bloqueantes. Archivado.

## 2026-11-16 — C-04 `persistencia-postgresql-y-docker`

- RED contra PostgreSQL 16 real: 11 fallas de concurrencia (turnos duplicados).
- GREEN: `FOR UPDATE`; suite completa contra PostgreSQL + Redis tres veces seguidas.
- Docker Compose validado con `docker compose config`; levantar los contenedores queda para la PC del alumno (sin acceso a Docker Hub en el entorno del agente). Archivado.

## 2026-11-16 — Segunda auditoría, contra el PDF de la consigna

Con el PDF del TPI a mano se revisó punto por punto. Hallazgos nuevos:

| # | Requisito del PDF | Hallazgo | Acción |
| --- | --- | --- | --- |
| A-07 | "Trabajen sobre el mismo proyecto y repositorio del Parcial 2 (...) Continúen con la modalidad y el equipo" | El TPI se hace solo y en un repo nuevo. | El alumno indicó que **el docente lo autorizó**. Se aclara en el README. |
| A-08 | "Mantengan claves, tokens y contraseñas fuera del repositorio, de la entrega y del video" | La clave de demostración estaba escrita en el código y en el README. | Corregido: se lee de `ODONTOLOGIA_CLAVE_DEMO`; las pruebas generan una al azar (C-03, design D3b). |
| A-09 | El README debe indicar "qué está completo y qué queda pendiente" y la "preparación de datos ficticios" | No había una sección explícita. | Secciones agregadas al README. |
| A-10 | Skill: "cómo la crearon —incluida la skill creadora utilizada—" | La skill decía basarse en la guía de skill-creator, pero no había evidencia de su uso. | Se usó `skill-creator` de verdad: `quick_validate`, descripción más explícita, el "por qué" de cada punto y 2 casos de prueba en `evals/` (ver `docs/skills-mcp/skill-propia.md`). |
| A-11 | "Archivar no sustituye probar (...) comprueben también el funcionamiento real" | Docker Compose y la pantalla de login no se ejecutaron todavía en la PC del alumno. | Pendiente de verificar en la PC del alumno (tiene Docker Desktop) antes de entregar. |
| A-12 | MCP: "cómo comprobaron la conexión y el uso de una herramienta real" | Sin evidencia. | El alumno conecta Context7; la consulta se documenta en `docs/skills-mcp/mcp-context7.md`. |

## 2026-11-18 — Verificación en la PC del alumno

- `verificar.ps1` en Windows: 65 pruebas de backend OK, 17 de frontend OK, build OK, OpenSpec 4/4 specs válidas → `TODO OK`. Resuelve la parte de A-11 sobre la pantalla de login.
- Flujo real en el navegador: login → agenda → salir, con login 200 y logout 204 (ver evidencia de C-03).
- Docker Desktop no estaba instalado; el alumno lo instaló y el agente levantó el stack completo con `docker compose up --build -d`: PostgreSQL y Redis sanos, backend y frontend arriba, flujo completo por el frontend (201/409/422/403/401) y datos verificados en PostgreSQL y Redis (ver evidencia de C-04). **A-11 resuelto.**

## 2026-11-18 — MCP Context7 conectado y usado

- El alumno conectó el conector Context7 en claude.ai; el agente comprobó la conexión (`connected`, herramientas habilitadas).
- Consultas reales con `resolve-library-id` y `query-docs`: proxy de Vite v6.4.5 (verificación de C-02) y `with_for_update()` de SQLAlchemy 2.0 (verificación de C-04). Resultado contrastado con el código; ambas decisiones coinciden con la documentación oficial. Detalle en `docs/skills-mcp/mcp-context7.md`. **A-12 resuelto.**

## Limitaciones conocidas (para no afirmar de más)

- En el entorno del agente **no había acceso** a PyPI, npm ni a la CLI de OpenSpec. Por eso:
  - las pruebas de backend se corrieron con las librerías obtenidas de sus repositorios oficiales (ver evidencia);
  - la estructura de `openspec/` se escribió siguiendo el formato de OpenSpec (luego validada en la PC del alumno, ver arriba);
  - `npm install` y `npm run build` se verificaron en la PC del alumno (ver arriba).
- `docker compose up --build` no se pudo ejecutar en el entorno del agente; se ejecutó en la PC del alumno el 2026-11-18.
- Las pruebas de PostgreSQL y Redis del agente usaron psycopg y redis-py obtenidos de sus repositorios oficiales, por no tener acceso a PyPI.
- Nada de esto acredita revisión humana: el alumno debe leer y verificar los artefactos.
