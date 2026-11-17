"""C-01 — Registrar turno sin solapamientos (capa de servicio).

Todos los datos son ficticios (ver odontologia/datos_demo.py).
"""

import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path

from odontologia.db import crear_motor, crear_sesiones, preparar_agenda
from odontologia.errores import ErrorTurno
from odontologia.servicio import registrar_turno


def turno(**cambios):
    datos = {
        "paciente_id": "PAC-001",
        "profesional_id": "PRO-001",
        "box_id": "BOX-1",
        "inicio": "2026-12-01T09:00:00-03:00",
        "fin": "2026-12-01T09:30:00-03:00",
    }
    datos.update(cambios)
    return datos


class BaseAgenda(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        url = f"sqlite:///{Path(self._tmp.name) / 'agenda.db'}"
        self.motor = crear_motor(url)
        preparar_agenda(self.motor)
        self.sesiones = crear_sesiones(self.motor)

    def tearDown(self):
        self.motor.dispose()
        self._tmp.cleanup()

    def registrar(self, **cambios):
        return registrar_turno(self.sesiones, turno(**cambios))

    def assertRechazo(self, codigo, campo=None, **cambios):
        with self.assertRaises(ErrorTurno) as ctx:
            self.registrar(**cambios)
        self.assertEqual(ctx.exception.codigo, codigo)
        if campo is not None:
            self.assertEqual(ctx.exception.campo, campo)
        return ctx.exception


class AltaValida(BaseAgenda):
    def test_registra_y_devuelve_instantes_en_utc(self):
        creado = self.registrar()
        self.assertGreater(creado["id"], 0)
        self.assertEqual(creado["inicio"], datetime(2026, 12, 1, 12, 0, tzinfo=timezone.utc))
        self.assertEqual(creado["fin"], datetime(2026, 12, 1, 12, 30, tzinfo=timezone.utc))
        self.assertEqual(creado["paciente_id"], "PAC-001")

    def test_persiste_al_reabrir_la_agenda(self):
        self.registrar()
        self.registrar(inicio="2026-12-01T10:00:00-03:00", fin="2026-12-01T10:45:00-03:00")
        otra = crear_sesiones(self.motor)
        with otra() as s:
            from odontologia.db import Turno
            self.assertEqual(s.query(Turno).count(), 2)

    def test_offsets_equivalentes_representan_el_mismo_instante(self):
        self.registrar()
        self.assertRechazo(
            "conflicto_profesional",
            box_id="BOX-2",
            inicio="2026-12-01T12:00:00+00:00",
            fin="2026-12-01T12:30:00Z",
        )


class EntradasInvalidas(BaseAgenda):
    def test_campos_obligatorios(self):
        for campo in ("paciente_id", "profesional_id", "box_id", "inicio", "fin"):
            with self.subTest(campo=campo):
                datos = turno()
                del datos[campo]
                with self.assertRaises(ErrorTurno) as ctx:
                    registrar_turno(self.sesiones, datos)
                self.assertEqual((ctx.exception.codigo, ctx.exception.campo), ("entrada_invalida", campo))

    def test_identificadores_mal_formados(self):
        for valor in ("", "  PAC-001", "PAC-001 ", 7, None, "X" * 65):
            with self.subTest(valor=valor):
                self.assertRechazo("entrada_invalida", "paciente_id", paciente_id=valor)

    def test_cuerpo_que_no_es_objeto(self):
        with self.assertRaises(ErrorTurno) as ctx:
            registrar_turno(self.sesiones, ["no", "es", "objeto"])
        self.assertEqual(ctx.exception.codigo, "entrada_invalida")

    def test_fecha_sin_offset_o_mal_escrita(self):
        for valor in ("2026-12-01T09:00:00", "01/12/2026 09:00", "", 20261201):
            with self.subTest(valor=valor):
                self.assertRechazo("entrada_invalida", "inicio", inicio=valor)

    def test_precision_de_minutos(self):
        self.assertRechazo("entrada_invalida", "inicio", inicio="2026-12-01T09:00:30-03:00")
        self.assertRechazo("entrada_invalida", "fin", fin="2026-12-01T09:30:00.500-03:00")

    def test_intervalo_vacio_o_invertido(self):
        self.assertRechazo("entrada_invalida", "fin", fin="2026-12-01T09:00:00-03:00")
        self.assertRechazo("entrada_invalida", "fin", fin="2026-12-01T08:30:00-03:00")

    def test_recursos_desconocidos_en_orden(self):
        self.assertRechazo("recurso_desconocido", "paciente_id", paciente_id="PAC-999", profesional_id="PRO-999")
        self.assertRechazo("recurso_desconocido", "profesional_id", profesional_id="PRO-999")
        self.assertRechazo("recurso_desconocido", "box_id", box_id="BOX-9")

    def test_rechazo_no_registra_nada(self):
        self.assertRechazo("recurso_desconocido", box_id="BOX-9")
        from odontologia.db import Turno
        with self.sesiones() as s:
            self.assertEqual(s.query(Turno).count(), 0)


class Solapamientos(BaseAgenda):
    SOLAPADOS = (
        ("mismo intervalo", "09:00", "09:30"),
        ("empieza antes", "08:45", "09:15"),
        ("termina despues", "09:15", "09:45"),
        ("contenido", "09:10", "09:20"),
        ("contiene", "08:30", "10:00"),
    )

    def setUp(self):
        super().setUp()
        self.registrar()  # PRO-001 en BOX-1, 09:00-09:30 (-03:00)

    def test_conflicto_de_profesional_con_otro_box(self):
        for nombre, ini, fin in self.SOLAPADOS:
            with self.subTest(nombre):
                self.assertRechazo(
                    "conflicto_profesional", "profesional_id",
                    paciente_id="PAC-002", box_id="BOX-2",
                    inicio=f"2026-12-01T{ini}:00-03:00", fin=f"2026-12-01T{fin}:00-03:00",
                )

    def test_conflicto_de_box_con_otro_profesional(self):
        for nombre, ini, fin in self.SOLAPADOS:
            with self.subTest(nombre):
                self.assertRechazo(
                    "conflicto_box", "box_id",
                    paciente_id="PAC-002", profesional_id="PRO-002",
                    inicio=f"2026-12-01T{ini}:00-03:00", fin=f"2026-12-01T{fin}:00-03:00",
                )

    def test_si_chocan_ambos_se_informa_primero_profesional(self):
        self.assertRechazo("conflicto_profesional", paciente_id="PAC-002")

    def test_turnos_adyacentes_se_permiten(self):
        antes = self.registrar(inicio="2026-12-01T08:30:00-03:00", fin="2026-12-01T09:00:00-03:00")
        despues = self.registrar(inicio="2026-12-01T09:30:00-03:00", fin="2026-12-01T10:00:00-03:00")
        self.assertNotEqual(antes["id"], despues["id"])

    def test_recursos_distintos_pueden_ser_simultaneos(self):
        creado = self.registrar(paciente_id="PAC-002", profesional_id="PRO-002", box_id="BOX-2")
        self.assertGreater(creado["id"], 1)

    def test_rechazo_conserva_el_turno_original(self):
        self.assertRechazo("conflicto_box", profesional_id="PRO-002")
        from odontologia.db import Turno
        with self.sesiones() as s:
            filas = s.query(Turno).all()
            self.assertEqual(len(filas), 1)
            self.assertEqual(filas[0].profesional_id, "PRO-001")


class Concurrencia(BaseAgenda):
    def test_dos_altas_simultaneas_del_mismo_profesional(self):
        barrera = threading.Barrier(2)
        resultados = []

        def intentar(box):
            sesiones = crear_sesiones(self.motor)
            barrera.wait()
            try:
                registrar_turno(sesiones, turno(box_id=box))
                resultados.append("ok")
            except ErrorTurno as e:
                resultados.append(e.codigo)

        hilos = [threading.Thread(target=intentar, args=(b,)) for b in ("BOX-1", "BOX-2")]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join(timeout=15)
        self.assertEqual(sorted(resultados), ["conflicto_profesional", "ok"])
        from odontologia.db import Turno
        with self.sesiones() as s:
            self.assertEqual(s.query(Turno).count(), 1)


if __name__ == "__main__":
    unittest.main()
