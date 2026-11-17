# Proposal — C-01 registrar-turno-sin-solapamientos

## Why

El problema central del Discovery es la doble reserva: hoy Recepción anota turnos a mano y puede asignar el mismo profesional o el mismo box a dos pacientes en horarios superpuestos (ver `discovery/discovery.md`, D-01). Es la funcionalidad base del roadmap: sin un alta confiable no tiene sentido consultar, cancelar ni recordar turnos.

## What Changes

- Nueva API local con FastAPI: `POST /turnos` y `GET /health`.
- Persistencia con SQLAlchemy sobre SQLite, con catálogo ficticio (2 pacientes, 2 profesionales, 2 boxes).
- Validación explícita de identificadores y fechas (zona horaria obligatoria, precisión de minutos, inicio < fin).
- Regla de no solapamiento por profesional (RN-01) y por box (RN-02) sobre intervalos `[inicio, fin)`, con adyacencia permitida.
- Errores con formato único `{error, campo, mensaje}` y códigos HTTP 201 / 404 / 409 / 422.
- Transacción `BEGIN IMMEDIATE` para que dos altas simultáneas no se registren ambas.
- Pruebas unitarias, de API y de concurrencia con `unittest`.

## Capabilities

### New Capabilities

- `registro-turnos`: alta validada y persistente de turnos sin solapamiento de profesional ni de box.

### Modified Capabilities

Ninguna (es el primer change del proyecto).

## Fuera de alcance

Consulta de agenda (C-02), autenticación JWT (C-03), cancelación y reprogramación (C-04), alta de pacientes (C-05), formulario web de alta (C-06), PostgreSQL (C-07), recordatorios (C-08), sobreturnos, historia clínica, pagos e integraciones externas.

## Impact

- Código nuevo en `backend/odontologia/` y `backend/tests/`.
- Dependencias: `fastapi`, `uvicorn`, `sqlalchemy`; `httpx` sólo para pruebas.
- La garantía de concurrencia aplica a procesos que usan este servicio sobre el mismo archivo SQLite local.
