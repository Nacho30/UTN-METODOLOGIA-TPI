# 07 — Decisiones

| ID | Decisión | Por qué | Origen | Estado |
| --- | --- | --- | --- | --- |
| DD-01 | Stack completo: Python, FastAPI, JWT, SQLAlchemy, PostgreSQL, Redis, Docker/Compose, React, TypeScript, Vite | Indicado por la cátedra (corrección del Parcial 2) | Consigna | Vigente |
| DD-02 | SQLite por defecto para desarrollo, PostgreSQL para Docker | Arrancar sin instalar nada; producción con PostgreSQL | C-01, C-04 | Vigente |
| DD-03 | Intervalo `[inicio, fin)` con adyacencia permitida | Práctica habitual de agendas | Discovery RN-03 | Vigente |
| DD-04 | Zona horaria obligatoria y guardado en UTC | Evita ambigüedades | C-01 D3 | Vigente |
| DD-05 | `BEGIN IMMEDIATE` para serializar altas | Evita doble reserva simultánea | C-01 D5 | Vigente |
| DD-06 | Prioridad: profesional antes que box | Determinismo | C-01 D4 | Vigente |
| DD-07 | Día del consultorio en UTC-03:00 fija | Argentina sin horario de verano | C-02 D1 | Vigente |
| DD-08 | Pruebas del frontend con `node:test` + `tsx` | Sin navegador, rápidas | C-02 D5 | Vigente |
| DD-09 | ~~Sin Redis ni Docker~~ | Revertida en la auditoría del 2026-11-16: repetía el error corregido en el Parcial 2 | Auditoría | **Reemplazada por DD-11 y DD-13** |
| DD-10 | Trabajo individual | El alumno hace el TPI solo | Alumno, 2026-11-16 | Vigente |
| DD-11 | JWT HS256 de 30 min con `jti`; logout guardando el `jti` en Redis con TTL | Stack de la cátedra y cierre de sesión real | C-03 | Vigente |
| DD-12 | Matriz de permisos: Recepción y Administración registran; los tres roles consultan | Resuelve Q04 | C-03 | Vigente |
| DD-13 | `SELECT … FOR UPDATE` profesional → box en PostgreSQL | Mantener RN-08 sin reintentos ni deadlocks | C-04 | Vigente |
| DD-14 | Docker Compose con PostgreSQL, Redis, backend y frontend; secretos en `.env` | Stack de la cátedra sin secretos en el repo | C-04 | Vigente |
