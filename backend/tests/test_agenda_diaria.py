"""C-02 — Consultar agenda diaria (servicio y GET /agenda)."""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from odontologia.api import crear_app
from odontologia.errores import ErrorTurno
from odontologia.servicio import consultar_agenda, registrar_turno


def alta(sesiones, inicio, fin, profesional="PRO-001", box="BOX-1", paciente="PAC-001"):
    return registrar_turno(sesiones, {
        "paciente_id": paciente, "profesional_id": profesional, "box_id": box,
        "inicio": inicio, "fin": fin,
    })


class BaseConTurnos(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.app = crear_app(f"sqlite:///{Path(self._tmp.name) / 'agenda.db'}")
        self.sesiones = self.app.state.sesiones
        self.cliente = TestClient(self.app)
        # Cargados desordenados a propósito. Hora del consultorio: -03:00.
        alta(self.sesiones, "2026-12-01T11:00:00-03:00", "2026-12-01T11:30:00-03:00", "PRO-002", "BOX-2", "PAC-002")
        alta(self.sesiones, "2026-12-01T09:00:00-03:00", "2026-12-01T09:30:00-03:00")
        alta(self.sesiones, "2026-12-01T09:00:00-03:00", "2026-12-01T09:45:00-03:00", "PRO-002", "BOX-2", "PAC-002")
        alta(self.sesiones, "2026-12-02T09:00:00-03:00", "2026-12-02T09:30:00-03:00")
        # 23:30 del 30/11 hasta 00:30 del 01/12: cruza la medianoche local.
        alta(self.sesiones, "2026-11-30T23:30:00-03:00", "2026-12-01T00:30:00-03:00", "PRO-001", "BOX-2")

    def tearDown(self):
        self.app.state.motor.dispose()
        self._tmp.cleanup()

    def horas(self, turnos):
        return [(t["inicio"].strftime("%d %H:%M"), t["profesional_id"]) for t in turnos]


class ServicioAgenda(BaseConTurnos):
    def test_devuelve_solo_el_dia_pedido_ordenado(self):
        turnos = consultar_agenda(self.sesiones, "2026-12-01")
        # Horas en UTC: 09:00 -03:00 == 12:00 UTC
        self.assertEqual(self.horas(turnos), [
            ("01 02:30", "PRO-001"),  # el que cruza medianoche
            ("01 12:00", "PRO-001"),
            ("01 12:00", "PRO-002"),
            ("01 14:00", "PRO-002"),
        ])

    def test_turno_que_cruza_medianoche_aparece_en_ambos_dias(self):
        dia_anterior = consultar_agenda(self.sesiones, "2026-11-30")
        self.assertEqual(self.horas(dia_anterior), [("01 02:30", "PRO-001")])

    def test_empate_de_hora_se_ordena_por_id(self):
        turnos = consultar_agenda(self.sesiones, "2026-12-01")
        mismos = [t["id"] for t in turnos if t["inicio"].strftime("%H:%M") == "12:00"]
        self.assertEqual(mismos, sorted(mismos))

    def test_filtra_por_profesional_y_por_box(self):
        por_profesional = consultar_agenda(self.sesiones, "2026-12-01", profesional_id="PRO-002")
        self.assertEqual({t["profesional_id"] for t in por_profesional}, {"PRO-002"})
        self.assertEqual(len(por_profesional), 2)
        por_box = consultar_agenda(self.sesiones, "2026-12-01", box_id="BOX-1")
        self.assertEqual(len(por_box), 1)
        ambos = consultar_agenda(self.sesiones, "2026-12-01", profesional_id="PRO-001", box_id="BOX-2")
        self.assertEqual(len(ambos), 1)

    def test_incluye_nombres_ficticios_para_mostrar(self):
        primero = consultar_agenda(self.sesiones, "2026-12-01", box_id="BOX-1")[0]
        self.assertEqual(primero["paciente_nombre"], "Paciente Ficticio Uno")
        self.assertEqual(primero["profesional_nombre"], "Odontóloga Ficticia A")
        self.assertEqual(primero["box_nombre"], "Box 1")

    def test_dia_sin_turnos_devuelve_lista_vacia(self):
        self.assertEqual(consultar_agenda(self.sesiones, "2026-12-25"), [])

    def test_fecha_invalida(self):
        for valor in ("", "01/12/2026", "2026-13-01", "2026-02-30", "20261201", None, 20261201):
            with self.subTest(valor=valor):
                with self.assertRaises(ErrorTurno) as ctx:
                    consultar_agenda(self.sesiones, valor)
                self.assertEqual((ctx.exception.codigo, ctx.exception.campo), ("entrada_invalida", "fecha"))

    def test_filtro_desconocido_o_mal_formado(self):
        casos = [
            ({"profesional_id": "PRO-999"}, "recurso_desconocido", "profesional_id"),
            ({"box_id": "BOX-9"}, "recurso_desconocido", "box_id"),
            ({"profesional_id": " PRO-001"}, "entrada_invalida", "profesional_id"),
            ({"box_id": ""}, "entrada_invalida", "box_id"),
        ]
        for filtros, codigo, campo in casos:
            with self.subTest(filtros=filtros):
                with self.assertRaises(ErrorTurno) as ctx:
                    consultar_agenda(self.sesiones, "2026-12-01", **filtros)
                self.assertEqual((ctx.exception.codigo, ctx.exception.campo), (codigo, campo))


class ApiAgenda(BaseConTurnos):
    def test_get_agenda_200(self):
        r = self.cliente.get("/agenda", params={"fecha": "2026-12-01", "profesional_id": "PRO-001"})
        self.assertEqual(r.status_code, 200)
        cuerpo = r.json()
        self.assertEqual(cuerpo["fecha"], "2026-12-01")
        self.assertEqual(cuerpo["zona_horaria"], "-03:00")
        self.assertEqual([t["inicio"] for t in cuerpo["turnos"]], ["2026-12-01T02:30:00Z", "2026-12-01T12:00:00Z"])

    def test_get_agenda_vacia_200(self):
        r = self.cliente.get("/agenda", params={"fecha": "2026-12-25"})
        self.assertEqual((r.status_code, r.json()["turnos"]), (200, []))

    def test_get_agenda_sin_fecha_422(self):
        r = self.cliente.get("/agenda")
        self.assertEqual(r.status_code, 422)
        self.assertEqual((r.json()["error"], r.json()["campo"]), ("entrada_invalida", "fecha"))

    def test_get_agenda_fecha_mal_escrita_422(self):
        r = self.cliente.get("/agenda", params={"fecha": "01/12/2026"})
        self.assertEqual(r.status_code, 422)

    def test_get_agenda_profesional_desconocido_404(self):
        r = self.cliente.get("/agenda", params={"fecha": "2026-12-01", "profesional_id": "PRO-999"})
        self.assertEqual((r.status_code, r.json()["error"]), (404, "recurso_desconocido"))

    def test_catalogo_para_filtros(self):
        r = self.cliente.get("/catalogo")
        self.assertEqual(r.status_code, 200)
        self.assertEqual([p["id"] for p in r.json()["profesionales"]], ["PRO-001", "PRO-002"])
        self.assertEqual([b["id"] for b in r.json()["boxes"]], ["BOX-1", "BOX-2"])


if __name__ == "__main__":
    unittest.main()
