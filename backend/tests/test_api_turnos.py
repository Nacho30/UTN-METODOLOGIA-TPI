"""C-01 — Adaptador HTTP de POST /turnos (FastAPI). Desde C-03 requiere sesión."""

import unittest

from .apoyo import BaseDeDatosDePrueba, cliente_con_sesion, nueva_app

TURNO = {
    "paciente_id": "PAC-001",
    "profesional_id": "PRO-001",
    "box_id": "BOX-1",
    "inicio": "2026-12-01T09:00:00-03:00",
    "fin": "2026-12-01T09:30:00-03:00",
}


class ApiTurnos(unittest.TestCase):
    def setUp(self):
        self.base = BaseDeDatosDePrueba()
        self.app = nueva_app(self.base)
        self.cliente = cliente_con_sesion(self.app, "recepcion")

    def tearDown(self):
        self.base.limpiar(self.app.state.motor)

    def test_health(self):
        r = self.cliente.get("/health")
        self.assertEqual((r.status_code, r.json()), (200, {"estado": "ok"}))

    def test_alta_devuelve_201_en_utc(self):
        r = self.cliente.post("/turnos", json=TURNO)
        self.assertEqual(r.status_code, 201)
        cuerpo = r.json()
        self.assertEqual(cuerpo["inicio"], "2026-12-01T12:00:00Z")
        self.assertEqual(cuerpo["fin"], "2026-12-01T12:30:00Z")
        self.assertEqual(cuerpo["id"], 1)

    def test_conflicto_devuelve_409(self):
        self.cliente.post("/turnos", json=TURNO)
        r = self.cliente.post("/turnos", json={**TURNO, "paciente_id": "PAC-002", "box_id": "BOX-2"})
        self.assertEqual(r.status_code, 409)
        self.assertEqual(r.json()["error"], "conflicto_profesional")

    def test_entrada_invalida_devuelve_422(self):
        r = self.cliente.post("/turnos", json={**TURNO, "inicio": "2026-12-01T09:00:00"})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()["error"], "entrada_invalida")
        self.assertEqual(r.json()["campo"], "inicio")

    def test_json_mal_formado_devuelve_422(self):
        r = self.cliente.post("/turnos", content=b"{no json", headers={"content-type": "application/json"})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.json()["error"], "entrada_invalida")

    def test_recurso_desconocido_devuelve_404(self):
        r = self.cliente.post("/turnos", json={**TURNO, "box_id": "BOX-9"})
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.json(), {
            "error": "recurso_desconocido",
            "campo": "box_id",
            "mensaje": "No existe box_id 'BOX-9' en el catálogo ficticio.",
        })


if __name__ == "__main__":
    unittest.main()
