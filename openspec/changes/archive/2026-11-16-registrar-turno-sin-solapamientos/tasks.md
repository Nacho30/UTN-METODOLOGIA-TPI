# Tasks — C-01 registrar-turno-sin-solapamientos

Cada tarea se marcó sólo después de ejecutar sus pruebas. Evidencia y comandos en `docs/evidencia/C-01-registrar-turno.md`.

## 1. Base del backend

- [x] 1.1 Crear `backend/` con `requirements.txt` (FastAPI, Uvicorn, SQLAlchemy, HTTPX para pruebas) y paquete `odontologia`.
- [x] 1.2 Escribir las pruebas de `tests/test_registro_turnos.py` y `tests/test_api_turnos.py` y ejecutarlas en RED (fallan por `ModuleNotFoundError: odontologia.db`).
- [x] 1.3 Modelos SQLAlchemy (`Paciente`, `Profesional`, `Box`, `Turno`) y `preparar_agenda` con catálogo ficticio que no borra turnos.

## 2. Validación de entrada

- [x] 2.1 Validar campos obligatorios e identificadores (vacío, tipo, espacios extremos, más de 64 caracteres) → `entrada_invalida` con campo.
- [x] 2.2 Validar fechas: zona horaria obligatoria, formato ISO, minutos exactos, `inicio < fin`; normalizar a UTC sin redondear.
- [x] 2.3 Verificar existencia de paciente, profesional y box en ese orden → `recurso_desconocido`.

## 3. Regla de no solapamiento

- [x] 3.1 Conflicto de profesional con cinco patrones de superposición (igual, empieza antes, termina después, contenido, contiene).
- [x] 3.2 Conflicto de box con los mismos patrones y prioridad de profesional cuando chocan ambos.
- [x] 3.3 Adyacencia permitida, recursos distintos simultáneos y offsets equivalentes (`-03:00` vs `Z`).
- [x] 3.4 Un rechazo no modifica la agenda.

## 4. Concurrencia

- [x] 4.1 Prueba con dos hilos y conexiones independientes sincronizados por barrera: un alta y un `conflicto_profesional`.
- [x] 4.2 `BEGIN IMMEDIATE` mediante eventos de SQLAlchemy; prueba de mutación con `BEGIN` común (falla) y con `BEGIN IMMEDIATE` (pasa 5/5).

## 5. API y cierre

- [x] 5.1 `POST /turnos` (201/404/409/422, JSON mal formado → 422) y `GET /health`; ejemplo de cuerpo en Swagger.
- [x] 5.2 Suite completa en verde, `ruff check` sin errores y prueba manual con Uvicorn + curl.
- [x] 5.3 Sincronizar `openspec/specs/registro-turnos/spec.md` y archivar el change.
