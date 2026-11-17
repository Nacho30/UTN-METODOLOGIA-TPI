# Tasks — C-02 consultar-agenda-diaria

Cada tarea se marcó sólo después de ejecutar sus pruebas. Evidencia y comandos en `docs/evidencia/C-02-agenda-diaria.md`.

## 1. Backend

- [x] 1.1 Escribir `tests/test_agenda_diaria.py` y ejecutarlo en RED (falla al importar `consultar_agenda`).
- [x] 1.2 `consultar_agenda`: validar `fecha` (formato exacto y fecha real) y calcular el día local `-03:00` en UTC.
- [x] 1.3 Incluir turnos que intersectan el día (cruce de medianoche) y ordenar por `(inicio, id)`.
- [x] 1.4 Filtros `profesional_id` y `box_id` combinables, con `entrada_invalida` y `recurso_desconocido`.
- [x] 1.5 Agregar nombres ficticios a cada turno y `listar_catalogo`.
- [x] 1.6 Endpoints `GET /agenda` y `GET /catalogo`; suite completa del backend en verde.

## 2. Frontend

- [x] 2.1 Proyecto Vite + React + TypeScript con proxy `/api` al backend.
- [x] 2.2 Escribir `src/agenda.test.ts` y luego `src/agenda.ts`: URL de consulta, hora y fecha locales, rango con cruce de medianoche, hoy en el consultorio y mensajes de error.
- [x] 2.3 Pantalla `App.tsx` con fecha, filtros, tabla y estados cargando / vacío / error.

## 3. Cierre

- [x] 3.1 Revisión del change con la skill `odontologia-turnos`.
- [x] 3.2 Suites de backend y frontend en verde; prueba manual de la API con Uvicorn.
- [x] 3.3 Sincronizar `openspec/specs/agenda-diaria/spec.md` y archivar el change.
