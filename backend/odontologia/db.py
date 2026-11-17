"""Persistencia con SQLAlchemy.

- SQLite (por defecto, C-01): cada transacción empieza con BEGIN IMMEDIATE, así
  la consulta de solapamientos y el INSERT quedan serializados entre conexiones
  que usan el mismo archivo.
- PostgreSQL (C-04): URL `postgresql+psycopg://...`; la serialización la da el
  bloqueo de filas SELECT ... FOR UPDATE en servicio.registrar_turno.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    event,
    select,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from . import datos_demo


class Base(DeclarativeBase):
    pass


class Paciente(Base):
    __tablename__ = "pacientes"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))


class Profesional(Base):
    __tablename__ = "profesionales"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))


class Box(Base):
    __tablename__ = "boxes"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))


class Usuario(Base):
    """Personal del consultorio (C-03). Sólo se guarda el hash de la clave."""

    __tablename__ = "usuarios"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120))
    rol: Mapped[str] = mapped_column(String(32))
    clave_hash: Mapped[str] = mapped_column(String(200))


class Turno(Base):
    """Turno con intervalo semiabierto [inicio, fin), guardado en UTC sin tzinfo."""

    __tablename__ = "turnos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paciente_id: Mapped[str] = mapped_column(ForeignKey("pacientes.id"))
    profesional_id: Mapped[str] = mapped_column(ForeignKey("profesionales.id"), index=True)
    box_id: Mapped[str] = mapped_column(ForeignKey("boxes.id"), index=True)
    inicio: Mapped[datetime] = mapped_column(DateTime, index=True)
    fin: Mapped[datetime] = mapped_column(DateTime)


def crear_motor(url: str) -> Engine:
    if not url.startswith("sqlite"):
        return create_engine(url, pool_pre_ping=True)

    motor = create_engine(url, connect_args={"timeout": 5, "check_same_thread": False})

    @event.listens_for(motor, "connect")
    def _sin_transaccion_implicita(conexion_dbapi, _registro):
        conexion_dbapi.isolation_level = None  # SQLAlchemy controla el BEGIN

    @event.listens_for(motor, "begin")
    def _begin_immediate(conexion):
        conexion.exec_driver_sql("BEGIN IMMEDIATE")

    return motor


def crear_sesiones(motor: Engine) -> sessionmaker:
    return sessionmaker(bind=motor, expire_on_commit=False)


def preparar_agenda(motor: Engine) -> None:
    """Crea las tablas y carga el catálogo ficticio si falta. Nunca borra turnos."""
    Base.metadata.create_all(motor)
    with crear_sesiones(motor)() as sesion, sesion.begin():
        for modelo, filas in (
            (Paciente, datos_demo.PACIENTES),
            (Profesional, datos_demo.PROFESIONALES),
            (Box, datos_demo.BOXES),
        ):
            existentes = set(sesion.scalars(select(modelo.id)))
            for id_, nombre in filas:
                if id_ not in existentes:
                    sesion.add(modelo(id=id_, nombre=nombre))
        usuarios = set(sesion.scalars(select(Usuario.id)))
        for id_, nombre, rol, clave_hash in datos_demo.USUARIOS:
            if id_ not in usuarios:
                sesion.add(Usuario(id=id_, nombre=nombre, rol=rol, clave_hash=clave_hash))
