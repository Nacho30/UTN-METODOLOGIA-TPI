# Instrucciones para agentes — UTN-METODOLOGIA-TPI

Sistema de agenda de turnos para un consultorio odontológico **ficticio**. TPI individual de Metodología I (UTN, comisión 3) de Ignacio Martín Rodríguez. `AGENTS.md` y `CLAUDE.md` deben ser idénticos.

## Antes de tocar nada

1. Leer [knowledge-base/README.md](knowledge-base/README.md) y los documentos que afecten la tarea.
2. Leer [ROADMAP.md](ROADMAP.md) y las dependencias del change.
3. Ejecutar `openspec list` para ver el estado real de los changes.

## Stack

| Parte | Tecnología | Carpeta |
| --- | --- | --- |
| Backend | Python 3.12+, FastAPI, SQLAlchemy | `backend/` |
| Autenticación | JWT (PyJWT) + Redis para sesiones cerradas | `backend/odontologia/autenticacion.py` |
| Base de datos | SQLite (desarrollo) y PostgreSQL (Docker) | `ODONTOLOGIA_DB_URL` |
| Contenedores | Docker / Docker Compose | `docker-compose.yml` |
| Frontend | React + TypeScript + Vite | `frontend/` |
| Especificación | OpenSpec | `openspec/` |

Es el stack que fijó la cátedra. No se quita ni se reemplaza ninguna tecnología sin una decisión registrada en `knowledge-base/07_decisiones.md`.

## Estado

- **C-01** `registrar-turno-sin-solapamientos`: archivado.
- **C-02** `consultar-agenda-diaria`: archivado.
- **C-03** `autenticar-personal-jwt`: archivado.
- **C-04** `persistencia-postgresql-y-docker`: archivado.
- C-05 a C-08: pendientes (ver roadmap).

## Flujo por change

`openspec-explore` → `openspec-propose` → revisión con `odontologia-turnos` → `openspec-apply-change` (TDD) → suite completa → revisión con `odontologia-turnos` → `openspec-archive-change`. Registro de skills: [.atl/skill-registry.md](.atl/skill-registry.md).

## Reglas duras

- **R-01 Datos:** sólo datos ficticios. Nunca datos reales de pacientes, secretos, tokens ni contraseñas reales en el repo. El secreto JWT, la clave de PostgreSQL y la clave de los usuarios ficticios (`ODONTOLOGIA_CLAVE_DEMO`) van sólo en `.env` o variables de entorno; tampoco se muestran en la entrega ni en el video.
- **R-02 Alcance:** no implementar nada fuera del `proposal.md` del change activo. Sin sobreturnos.
- **R-03 Capas:** reglas de negocio sólo en `backend/odontologia/servicio.py` y permisos sólo en `backend/odontologia/autenticacion.py`; código de backend sólo en `backend/` y de interfaz sólo en `frontend/`.
- **R-04 Contrato:** no cambiar en silencio el intervalo `[inicio, fin)`, el uso de UTC, la zona UTC-03:00, los códigos de error ni la matriz de permisos. Un cambio de contrato requiere un change nuevo.
- **R-04b Seguridad:** toda ruta nueva exige sesión JWT salvo que la spec diga lo contrario.
- **R-05 Errores:** validar explícitamente y responder `{error, campo, mensaje}`. No corregir datos inválidos para aceptarlos.
- **R-06 Pruebas:** RED antes de GREEN; cubrir todos los escenarios de la spec; no archivar con pruebas fallando. Una prueba secuencial no demuestra concurrencia. Lo que toque la base se prueba también con `ODONTOLOGIA_TEST_DB_URL` (PostgreSQL).
- **R-07 Evidencia:** registrar comandos y resultados reales en `docs/evidencia/`. No afirmar pruebas, revisiones humanas ni resultados que no ocurrieron.
- **R-08 Integraciones:** sin servicios externos reales (WhatsApp, AFIP/ARCA, obras sociales). PostgreSQL y Redis corren locales o en Docker Compose.
- **R-09 Git:** commits descriptivos; no publicar sin autorización del alumno.

## Comandos

```bash
# Backend (desde backend/)
python -m unittest discover -s tests -t .
ODONTOLOGIA_TEST_DB_URL=postgresql+psycopg://... python -m unittest discover -s tests -t .
uvicorn odontologia.api:crear_app --factory --reload

# Todo el stack
docker compose up --build

# Frontend (desde frontend/)
npm test
npm run dev
```
