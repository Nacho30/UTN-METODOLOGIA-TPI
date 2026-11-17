"""API HTTP local (FastAPI). Ejecutar desde backend/:

    uvicorn odontologia.api:crear_app --factory --reload

La URL de la base se toma de ODONTOLOGIA_DB_URL (por defecto SQLite local).
"""

import json
import os
from datetime import datetime, timezone

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse

from .db import crear_motor, crear_sesiones, preparar_agenda
from .errores import ErrorTurno
from .servicio import NOMBRE_ZONA, consultar_agenda, listar_catalogo, registrar_turno

URL_POR_DEFECTO = "sqlite:///./odontologia.db"

EJEMPLO_TURNO = {
    "paciente_id": "PAC-001",
    "profesional_id": "PRO-001",
    "box_id": "BOX-1",
    "inicio": "2026-12-01T09:00:00-03:00",
    "fin": "2026-12-01T09:30:00-03:00",
}

DOC_CUERPO_TURNO = {
    "requestBody": {
        "required": True,
        "content": {"application/json": {
            "schema": {
                "type": "object",
                "required": list(EJEMPLO_TURNO),
                "properties": {campo: {"type": "string"} for campo in EJEMPLO_TURNO},
            },
            "example": EJEMPLO_TURNO,
        }},
    }
}


def iso_utc(instante: datetime) -> str:
    return instante.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serializar(turno: dict) -> dict:
    return {**turno, "inicio": iso_utc(turno["inicio"]), "fin": iso_utc(turno["fin"])}


def crear_app(url_db: str | None = None) -> FastAPI:
    motor = crear_motor(url_db or os.environ.get("ODONTOLOGIA_DB_URL", URL_POR_DEFECTO))
    preparar_agenda(motor)
    sesiones = crear_sesiones(motor)

    app = FastAPI(
        title="Sistema odontológico — Agenda de turnos",
        version="0.2.0",
        description="API local del TPI de Metodología I. Sólo datos ficticios.",
    )
    app.state.motor = motor
    app.state.sesiones = sesiones

    @app.exception_handler(ErrorTurno)
    async def _error_turno(_request: Request, error: ErrorTurno):
        return JSONResponse(status_code=error.estado_http, content=error.como_dict())

    @app.get("/health")
    def health():
        return {"estado": "ok"}

    @app.post("/turnos", status_code=201, openapi_extra=DOC_CUERPO_TURNO)
    async def crear_turno(request: Request):
        # Se lee el cuerpo crudo para que TODO error de forma use el mismo
        # formato {error, campo, mensaje} definido en la spec.
        try:
            datos = json.loads(await request.body() or b"null")
        except ValueError:
            raise ErrorTurno("entrada_invalida", None, "El cuerpo no es JSON válido.") from None
        return serializar(registrar_turno(sesiones, datos))

    @app.get("/agenda")
    def agenda(
        fecha: str | None = Query(None, description="Día local del consultorio, AAAA-MM-DD", examples=["2026-12-01"]),
        profesional_id: str | None = Query(None, examples=["PRO-001"]),
        box_id: str | None = Query(None, examples=["BOX-1"]),
    ):
        turnos = consultar_agenda(sesiones, fecha, profesional_id=profesional_id, box_id=box_id)
        return {
            "fecha": fecha,
            "zona_horaria": NOMBRE_ZONA,
            "turnos": [serializar(t) for t in turnos],
        }

    @app.get("/catalogo")
    def catalogo():
        return listar_catalogo(sesiones)

    return app

