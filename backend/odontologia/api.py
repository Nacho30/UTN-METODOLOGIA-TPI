"""API HTTP local (FastAPI). Ejecutar desde backend/:

    uvicorn odontologia.api:crear_app --factory --reload

Configuración por variables de entorno:
- ODONTOLOGIA_DB_URL: base de datos (por defecto SQLite local).
- ODONTOLOGIA_JWT_SECRETO: secreto para firmar los JWT (mínimo 32 caracteres).
  Si falta, se genera uno al azar al iniciar y las sesiones se pierden al reiniciar.
- ODONTOLOGIA_REDIS_URL: Redis para guardar las sesiones cerradas (opcional).
"""

import json
import os
import secrets
import warnings
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import autenticacion as auth
from .db import Usuario, crear_motor, crear_sesiones, preparar_agenda
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

EJEMPLO_LOGIN = {"usuario": "recepcion", "clave": "Clave-Demo-2026"}
DOC_CUERPO_LOGIN = {
    "requestBody": {
        "required": True,
        "content": {"application/json": {
            "schema": {
                "type": "object",
                "required": ["usuario", "clave"],
                "properties": {"usuario": {"type": "string"}, "clave": {"type": "string"}},
            },
            "example": EJEMPLO_LOGIN,
        }},
    }
}

esquema_bearer = HTTPBearer(auto_error=False, description="Pegar el access_token de POST /auth/login")


async def leer_json(request: Request):
    """Lee el cuerpo crudo para que todo error de forma use {error, campo, mensaje}."""
    try:
        return json.loads(await request.body() or b"null")
    except ValueError:
        raise ErrorTurno("entrada_invalida", None, "El cuerpo no es JSON válido.") from None


def iso_utc(instante: datetime) -> str:
    return instante.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def serializar(turno: dict) -> dict:
    return {**turno, "inicio": iso_utc(turno["inicio"]), "fin": iso_utc(turno["fin"])}


def _secreto_configurado(secreto_jwt: str | None) -> str:
    secreto = secreto_jwt or os.environ.get("ODONTOLOGIA_JWT_SECRETO")
    if secreto is None:
        warnings.warn("ODONTOLOGIA_JWT_SECRETO no está definido: se usa un secreto temporal.", stacklevel=2)
        secreto = secrets.token_urlsafe(48)
    return auth.validar_secreto(secreto)


def crear_app(
    url_db: str | None = None,
    *,
    secreto_jwt: str | None = None,
    redis_url: str | None = None,
    minutos_token: int = auth.MINUTOS_TOKEN,
) -> FastAPI:
    secreto = _secreto_configurado(secreto_jwt)
    revocaciones = auth.crear_revocaciones(redis_url or os.environ.get("ODONTOLOGIA_REDIS_URL"))
    motor = crear_motor(url_db or os.environ.get("ODONTOLOGIA_DB_URL", URL_POR_DEFECTO))
    preparar_agenda(motor)
    sesiones = crear_sesiones(motor)

    app = FastAPI(
        title="Sistema odontológico — Agenda de turnos",
        version="0.4.0",
        description="API local del TPI de Metodología I. Sólo datos ficticios.",
    )
    app.state.motor = motor
    app.state.sesiones = sesiones
    app.state.revocaciones = revocaciones

    @app.exception_handler(ErrorTurno)
    async def _error_turno(_request: Request, error: ErrorTurno):
        cabeceras = {"WWW-Authenticate": "Bearer"} if error.estado_http == 401 else None
        return JSONResponse(status_code=error.estado_http, content=error.como_dict(), headers=cabeceras)

    def sesion_actual(credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)]) -> dict:
        if credenciales is None:
            raise ErrorTurno("no_autenticado", None, "Falta iniciar sesión (cabecera Authorization: Bearer).")
        return auth.leer_token(credenciales.credentials, secreto, revocaciones)

    def permiso(operacion: str):
        def _verificar(datos: Annotated[dict, Depends(sesion_actual)]) -> dict:
            auth.exigir_permiso(datos, operacion)
            return datos
        return _verificar

    # ------------------------------------------------------------ C-03 sesión

    @app.post("/auth/login", tags=["sesión"], openapi_extra=DOC_CUERPO_LOGIN)
    async def login(request: Request):
        usuario_id, clave = auth.validar_login(await leer_json(request))
        with sesiones() as sesion:
            usuario = sesion.get(Usuario, usuario_id)
        if usuario is None or not auth.verificar_clave(clave, usuario.clave_hash):
            raise auth.credenciales_invalidas()
        return {
            "access_token": auth.emitir_token(usuario.id, usuario.rol, secreto, minutos_token),
            "token_type": "bearer",
            "expira_en": minutos_token * 60,
            "usuario": usuario.id,
            "rol": usuario.rol,
        }

    @app.post("/auth/logout", tags=["sesión"], status_code=204)
    def logout(datos: Annotated[dict, Depends(sesion_actual)]):
        revocaciones.revocar(datos["jti"], datos["exp"])
        return Response(status_code=204)

    @app.get("/auth/yo", tags=["sesión"])
    def yo(datos: Annotated[dict, Depends(sesion_actual)]):
        with sesiones() as sesion:
            usuario = sesion.get(Usuario, datos["sub"])
        if usuario is None:
            raise ErrorTurno("token_invalido", None, "El usuario de la sesión ya no existe.")
        return {"usuario": usuario.id, "nombre": usuario.nombre, "rol": usuario.rol}

    @app.get("/health")
    def health():
        return {"estado": "ok"}

    @app.post("/turnos", status_code=201, tags=["agenda"], openapi_extra=DOC_CUERPO_TURNO,
              dependencies=[Depends(permiso("registrar_turno"))])
    async def crear_turno(request: Request):
        return serializar(registrar_turno(sesiones, await leer_json(request)))

    @app.get("/agenda", tags=["agenda"], dependencies=[Depends(permiso("consultar_agenda"))])
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

    @app.get("/catalogo", tags=["agenda"], dependencies=[Depends(permiso("consultar_agenda"))])
    def catalogo():
        return listar_catalogo(sesiones)

    return app

