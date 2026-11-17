"""Utilidades compartidas por las pruebas.

Por defecto cada prueba usa un archivo SQLite temporal. Si se define
ODONTOLOGIA_TEST_DB_URL (por ejemplo una base PostgreSQL vacía y descartable),
toda la suite corre contra esa base: se crea el esquema antes de cada prueba y
se borra después.
"""

import os
import secrets
import tempfile
from pathlib import Path

from fastapi.testclient import TestClient

from odontologia.api import crear_app
from odontologia.db import Base

SECRETO_PRUEBA = "secreto-de-prueba-ficticio-de-32-caracteres-o-mas"
# Clave de los usuarios ficticios: al azar en cada corrida, nunca escrita en el repo.
CLAVE_PRUEBA = secrets.token_urlsafe(12)
URL_EXTERNA = os.environ.get("ODONTOLOGIA_TEST_DB_URL")


class BaseDeDatosDePrueba:
    """Da una URL de base limpia y la limpia al final."""

    def __init__(self):
        self._tmp = None
        if URL_EXTERNA:
            self.url = URL_EXTERNA
        else:
            self._tmp = tempfile.TemporaryDirectory()
            self.url = f"sqlite:///{Path(self._tmp.name) / 'agenda.db'}"

    def limpiar(self, motor):
        if URL_EXTERNA:
            Base.metadata.drop_all(motor)
        motor.dispose()
        if self._tmp:
            self._tmp.cleanup()


def nueva_app(base: BaseDeDatosDePrueba, **opciones):
    opciones.setdefault("secreto_jwt", SECRETO_PRUEBA)
    opciones.setdefault("clave_demo", CLAVE_PRUEBA)
    if URL_EXTERNA:
        # La base externa puede tener restos de una corrida interrumpida.
        from odontologia.db import crear_motor

        motor = crear_motor(base.url)
        Base.metadata.drop_all(motor)
        motor.dispose()
    return crear_app(base.url, **opciones)


def iniciar_sesion(cliente: TestClient, usuario: str = "recepcion", clave: str = CLAVE_PRUEBA) -> str:
    respuesta = cliente.post("/auth/login", json={"usuario": usuario, "clave": clave})
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["access_token"]


def cliente_con_sesion(app, usuario: str = "recepcion") -> TestClient:
    cliente = TestClient(app)
    cliente.headers["Authorization"] = f"Bearer {iniciar_sesion(cliente, usuario)}"
    return cliente
