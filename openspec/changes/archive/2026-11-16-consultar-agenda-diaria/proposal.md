# Proposal — C-02 consultar-agenda-diaria

## Why

Con C-01 los turnos se registran sin choques, pero Recepción todavía no puede ver qué tiene cada día. El Discovery (D-02) pide "ver de un vistazo la agenda del día por profesional y por box". Además, es el primer change que usa el frontend del stack (React + TypeScript + Vite).

## What Changes

- `GET /agenda?fecha=AAAA-MM-DD` con filtros opcionales `profesional_id` y `box_id`.
- Día interpretado en hora del consultorio (UTC-03:00 fija); se incluyen los turnos que cruzan la medianoche.
- Orden estable por inicio e id; nombres ficticios de paciente, profesional y box para mostrar.
- `GET /catalogo` para llenar los filtros.
- Pantalla React "Agenda del día": fecha, filtros, tabla, estados cargando / vacío / error.
- Pruebas de backend (`unittest`) y de la lógica del frontend (`node:test` con `tsx`).

## Capabilities

### New Capabilities

- `agenda-diaria`: consulta de los turnos de un día con filtros, por API y por pantalla web.

### Modified Capabilities

Ninguna. `registro-turnos` no cambia: C-02 sólo lee turnos.

## Fuera de alcance

Vista semanal, alta de turnos desde la pantalla (C-06), login (C-03), zonas horarias configurables y paginación.

## Impact

- Backend: `servicio.consultar_agenda`, `servicio.listar_catalogo` y dos endpoints nuevos en `api.py`.
- Frontend nuevo en `frontend/` (React 19, TypeScript, Vite 6) con proxy `/api` → `127.0.0.1:8000`.
- Sin cambios de esquema de base de datos.
