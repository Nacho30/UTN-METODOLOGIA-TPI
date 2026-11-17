"""Reglas de negocio de la agenda. La API sólo adapta HTTP a estas funciones."""

import re
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from .db import Box, Paciente, Profesional, Turno
from .errores import ErrorTurno

LARGO_MAXIMO_ID = 64
# El consultorio (ficticio) opera en hora de Argentina, UTC-03:00 sin horario de verano.
ZONA_CONSULTORIO = timezone(timedelta(hours=-3))
NOMBRE_ZONA = "-03:00"
FORMATO_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")
RECURSOS = (
    ("paciente_id", Paciente),
    ("profesional_id", Profesional),
    ("box_id", Box),
)


# ---------------------------------------------------------------- validación

def _invalida(campo: str | None, mensaje: str) -> ErrorTurno:
    return ErrorTurno("entrada_invalida", campo, mensaje)


def _validar_id(datos: dict, campo: str) -> str:
    valor = datos.get(campo)
    if campo not in datos:
        raise _invalida(campo, f"Falta {campo}.")
    if not isinstance(valor, str) or not valor or valor != valor.strip() or len(valor) > LARGO_MAXIMO_ID:
        raise _invalida(
            campo,
            f"{campo} debe ser un texto no vacío, sin espacios al inicio o al final "
            f"y de hasta {LARGO_MAXIMO_ID} caracteres.",
        )
    return valor


def _validar_instante(datos: dict, campo: str) -> datetime:
    if campo not in datos:
        raise _invalida(campo, f"Falta {campo}.")
    valor = datos[campo]
    if not isinstance(valor, str):
        raise _invalida(campo, f"{campo} debe ser una fecha-hora ISO 8601 en texto.")
    try:
        instante = datetime.fromisoformat(valor)
    except ValueError:
        raise _invalida(campo, f"{campo} no es una fecha-hora ISO 8601 válida.") from None
    if instante.tzinfo is None or instante.utcoffset() is None:
        raise _invalida(campo, f"{campo} debe incluir zona horaria (por ejemplo -03:00 o Z).")
    if instante.second or instante.microsecond:
        raise _invalida(campo, f"{campo} debe tener precisión de minutos (segundos en cero).")
    return instante.astimezone(timezone.utc)


def validar_alta(datos) -> dict:
    """Valida la forma de la solicitud y devuelve los datos normalizados a UTC."""
    if not isinstance(datos, dict):
        raise _invalida(None, "El cuerpo debe ser un objeto JSON.")
    limpio = {campo: _validar_id(datos, campo) for campo, _ in RECURSOS}
    limpio["inicio"] = _validar_instante(datos, "inicio")
    limpio["fin"] = _validar_instante(datos, "fin")
    if limpio["inicio"] >= limpio["fin"]:
        raise _invalida("fin", "fin debe ser posterior a inicio.")
    return limpio


# ---------------------------------------------------------------- utilidades

def a_utc_naive(instante: datetime) -> datetime:
    return instante.astimezone(timezone.utc).replace(tzinfo=None)


def turno_a_dict(turno: Turno) -> dict:
    return {
        "id": turno.id,
        "paciente_id": turno.paciente_id,
        "profesional_id": turno.profesional_id,
        "box_id": turno.box_id,
        "inicio": turno.inicio.replace(tzinfo=timezone.utc),
        "fin": turno.fin.replace(tzinfo=timezone.utc),
    }


def _hay_solapamiento(sesion, columna, valor, inicio, fin) -> bool:
    """[inicio, fin) se solapa con un turno existente si existente.inicio < fin y existente.fin > inicio."""
    consulta = select(Turno.id).where(columna == valor, Turno.inicio < fin, Turno.fin > inicio).limit(1)
    return sesion.scalar(consulta) is not None


# ---------------------------------------------------------------- C-01

def registrar_turno(sesiones: sessionmaker, datos) -> dict:
    """Registra un turno si el profesional y el box están libres en [inicio, fin).

    Orden de evaluación: forma de los datos → existencia de recursos
    (paciente, profesional, box) → conflicto de profesional → conflicto de box.
    La verificación y el INSERT ocurren en la misma transacción.
    """
    limpio = validar_alta(datos)
    inicio, fin = a_utc_naive(limpio["inicio"]), a_utc_naive(limpio["fin"])

    with sesiones() as sesion, sesion.begin():
        for campo, modelo in RECURSOS:
            consulta = select(modelo.id).where(modelo.id == limpio[campo])
            if modelo is not Paciente:
                # C-04: en PostgreSQL bloquea la fila del profesional y del box hasta el
                # COMMIT, así otra alta del mismo recurso espera y luego ve este turno.
                # Siempre se bloquea profesional y después box: no hay ciclos (deadlock).
                # SQLite ignora FOR UPDATE; ahí serializa BEGIN IMMEDIATE (C-01).
                consulta = consulta.with_for_update()
            if sesion.scalar(consulta) is None:
                raise ErrorTurno(
                    "recurso_desconocido", campo,
                    f"No existe {campo} '{limpio[campo]}' en el catálogo ficticio.",
                )
        if _hay_solapamiento(sesion, Turno.profesional_id, limpio["profesional_id"], inicio, fin):
            raise ErrorTurno(
                "conflicto_profesional", "profesional_id",
                "El profesional ya tiene un turno que se superpone con ese horario.",
            )
        if _hay_solapamiento(sesion, Turno.box_id, limpio["box_id"], inicio, fin):
            raise ErrorTurno(
                "conflicto_box", "box_id",
                "El box ya está ocupado en ese horario.",
            )
        nuevo = Turno(
            paciente_id=limpio["paciente_id"],
            profesional_id=limpio["profesional_id"],
            box_id=limpio["box_id"],
            inicio=inicio,
            fin=fin,
        )
        sesion.add(nuevo)
        sesion.flush()
        return turno_a_dict(nuevo)


# ---------------------------------------------------------------- C-02

def _validar_fecha(valor) -> date:
    if not isinstance(valor, str) or not FORMATO_FECHA.fullmatch(valor):
        raise _invalida("fecha", "fecha es obligatoria y debe tener el formato AAAA-MM-DD.")
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise _invalida("fecha", f"La fecha {valor} no existe en el calendario.") from None


def consultar_agenda(sesiones: sessionmaker, fecha, profesional_id=None, box_id=None) -> list[dict]:
    """Turnos que ocupan parte del día local `fecha`, ordenados por inicio e id.

    El día es [00:00, 24:00) en ZONA_CONSULTORIO. Un turno que cruza la
    medianoche aparece en los dos días que toca.
    """
    dia = _validar_fecha(fecha)
    filtros = {}
    for campo, valor in (("profesional_id", profesional_id), ("box_id", box_id)):
        if valor is not None:
            filtros[campo] = _validar_id({campo: valor}, campo)

    desde = datetime.combine(dia, datetime.min.time(), ZONA_CONSULTORIO)
    hasta = desde + timedelta(days=1)
    desde, hasta = a_utc_naive(desde), a_utc_naive(hasta)

    with sesiones() as sesion:
        for campo, modelo in (("profesional_id", Profesional), ("box_id", Box)):
            if campo in filtros and sesion.get(modelo, filtros[campo]) is None:
                raise ErrorTurno(
                    "recurso_desconocido", campo,
                    f"No existe {campo} '{filtros[campo]}' en el catálogo ficticio.",
                )
        consulta = (
            select(Turno, Paciente.nombre, Profesional.nombre, Box.nombre)
            .join(Paciente, Paciente.id == Turno.paciente_id)
            .join(Profesional, Profesional.id == Turno.profesional_id)
            .join(Box, Box.id == Turno.box_id)
            .where(Turno.inicio < hasta, Turno.fin > desde)
            .order_by(Turno.inicio, Turno.id)
        )
        if "profesional_id" in filtros:
            consulta = consulta.where(Turno.profesional_id == filtros["profesional_id"])
        if "box_id" in filtros:
            consulta = consulta.where(Turno.box_id == filtros["box_id"])

        return [
            {**turno_a_dict(turno), "paciente_nombre": paciente,
             "profesional_nombre": profesional, "box_nombre": box}
            for turno, paciente, profesional, box in sesion.execute(consulta)
        ]


def listar_catalogo(sesiones: sessionmaker) -> dict:
    """Profesionales y boxes ficticios, para poblar los filtros del frontend."""
    with sesiones() as sesion:
        return {
            "profesionales": [{"id": p.id, "nombre": p.nombre}
                              for p in sesion.scalars(select(Profesional).order_by(Profesional.id))],
            "boxes": [{"id": b.id, "nombre": b.nombre}
                      for b in sesion.scalars(select(Box).order_by(Box.id))],
        }
