"""C-03 — Autenticar al personal con JWT y cerrar sesión con Redis."""

import os
import time
import unittest
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from odontologia.autenticacion import (
    PERMISOS,
    RevocacionesMemoria,
    RevocacionesRedis,
    hashear_clave,
    verificar_clave,
)
from odontologia.datos_demo import CLAVE_DEMO
from odontologia.db import crear_motor

from .apoyo import (
    SECRETO_PRUEBA,
    BaseDeDatosDePrueba,
    cliente_con_sesion,
    iniciar_sesion,
    nueva_app,
)

TURNO = {
    "paciente_id": "PAC-001",
    "profesional_id": "PRO-001",
    "box_id": "BOX-1",
    "inicio": "2026-12-01T09:00:00-03:00",
    "fin": "2026-12-01T09:30:00-03:00",
}


class Claves(unittest.TestCase):
    def test_hash_y_verificacion(self):
        guardado = hashear_clave("clave-ficticia")
        self.assertTrue(guardado.startswith("pbkdf2_sha256$"))
        self.assertNotIn("clave-ficticia", guardado)
        self.assertTrue(verificar_clave("clave-ficticia", guardado))
        self.assertFalse(verificar_clave("otra-clave", guardado))

    def test_misma_clave_genera_hash_distinto(self):
        self.assertNotEqual(hashear_clave("x"), hashear_clave("x"))

    def test_hash_mal_formado_no_valida(self):
        for guardado in ("", "texto", "md5$1$aa$bb", "pbkdf2_sha256$no-numero$aa$bb"):
            with self.subTest(guardado=guardado):
                self.assertFalse(verificar_clave("x", guardado))


class Matriz(unittest.TestCase):
    def test_matriz_de_permisos(self):
        self.assertEqual(PERMISOS["registrar_turno"], {"recepcion", "administracion"})
        self.assertEqual(PERMISOS["consultar_agenda"], {"recepcion", "profesional", "administracion"})


class BaseApi(unittest.TestCase):
    def setUp(self):
        self.base = BaseDeDatosDePrueba()
        self.app = nueva_app(self.base)
        self.cliente = TestClient(self.app)

    def tearDown(self):
        self.base.limpiar(self.app.state.motor)

    def token_a_mano(self, **cambios):
        ahora = datetime.now(timezone.utc)
        datos = {"sub": "recepcion", "rol": "recepcion", "jti": uuid.uuid4().hex,
                 "iat": ahora, "exp": ahora + timedelta(minutes=5)}
        datos.update(cambios)
        secreto = datos.pop("_secreto", SECRETO_PRUEBA)
        return jwt.encode(datos, secreto, algorithm="HS256")

    def assertError(self, respuesta, estado, codigo):
        self.assertEqual(respuesta.status_code, estado, respuesta.text)
        self.assertEqual(respuesta.json()["error"], codigo)


class Login(BaseApi):
    def test_login_correcto_devuelve_jwt_con_rol(self):
        r = self.cliente.post("/auth/login", json={"usuario": "recepcion", "clave": CLAVE_DEMO})
        self.assertEqual(r.status_code, 200)
        cuerpo = r.json()
        self.assertEqual((cuerpo["token_type"], cuerpo["rol"], cuerpo["usuario"]), ("bearer", "recepcion", "recepcion"))
        self.assertEqual(cuerpo["expira_en"], 30 * 60)
        datos = jwt.decode(cuerpo["access_token"], SECRETO_PRUEBA, algorithms=["HS256"])
        self.assertEqual((datos["sub"], datos["rol"]), ("recepcion", "recepcion"))
        self.assertIn("jti", datos)

    def test_cada_rol_puede_iniciar_sesion(self):
        for usuario, rol in (("recepcion", "recepcion"), ("profesional", "profesional"), ("admin", "administracion")):
            with self.subTest(usuario=usuario):
                r = self.cliente.post("/auth/login", json={"usuario": usuario, "clave": CLAVE_DEMO})
                self.assertEqual(r.json()["rol"], rol)

    def test_clave_incorrecta_y_usuario_inexistente_dan_el_mismo_error(self):
        a = self.cliente.post("/auth/login", json={"usuario": "recepcion", "clave": "incorrecta"})
        b = self.cliente.post("/auth/login", json={"usuario": "nadie", "clave": "incorrecta"})
        self.assertError(a, 401, "credenciales_invalidas")
        self.assertEqual(a.json(), b.json())

    def test_login_con_datos_mal_formados(self):
        for cuerpo in ({}, {"usuario": "recepcion"}, {"usuario": "", "clave": "x"}, {"usuario": 1, "clave": "x"}, []):
            with self.subTest(cuerpo=cuerpo):
                self.assertError(self.cliente.post("/auth/login", json=cuerpo), 422, "entrada_invalida")

    def test_yo_devuelve_el_usuario_de_la_sesion(self):
        cliente = cliente_con_sesion(self.app, "profesional")
        r = cliente.get("/auth/yo")
        self.assertEqual(r.json(), {"usuario": "profesional", "nombre": "Odontóloga Ficticia A", "rol": "profesional"})


class ProteccionDeRutas(BaseApi):
    def test_sin_token(self):
        for metodo, ruta in (("post", "/turnos"), ("get", "/agenda?fecha=2026-12-01"), ("get", "/catalogo"), ("get", "/auth/yo")):
            with self.subTest(ruta=ruta):
                r = getattr(self.cliente, metodo)(ruta, json=TURNO) if metodo == "post" else self.cliente.get(ruta)
                self.assertError(r, 401, "no_autenticado")
                self.assertEqual(r.headers.get("www-authenticate"), "Bearer")

    def test_health_es_publico(self):
        self.assertEqual(self.cliente.get("/health").status_code, 200)

    def test_tokens_invalidos(self):
        casos = {
            "basura": "no-es-un-jwt",
            "otro secreto": self.token_a_mano(_secreto="otro-secreto-ficticio-de-32-caracteres-xx"),
            "vencido": self.token_a_mano(exp=datetime.now(timezone.utc) - timedelta(seconds=1)),
            "sin jti": self.token_a_mano(jti=None),
            "rol inexistente": self.token_a_mano(rol="director"),
            "algoritmo none": jwt.encode({"sub": "recepcion", "rol": "recepcion", "jti": "x",
                                          "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
                                         None, algorithm="none"),
        }
        for nombre, token in casos.items():
            with self.subTest(nombre):
                r = self.cliente.get("/agenda?fecha=2026-12-01", headers={"Authorization": f"Bearer {token}"})
                self.assertError(r, 401, "token_invalido")

    def test_esquema_que_no_es_bearer(self):
        r = self.cliente.get("/catalogo", headers={"Authorization": "Basic abc"})
        self.assertError(r, 401, "no_autenticado")

    def test_profesional_no_puede_registrar_turnos(self):
        cliente = cliente_con_sesion(self.app, "profesional")
        self.assertError(cliente.post("/turnos", json=TURNO), 403, "sin_permiso")
        self.assertEqual(cliente.get("/agenda?fecha=2026-12-01").status_code, 200)

    def test_recepcion_y_administracion_registran(self):
        r1 = cliente_con_sesion(self.app, "recepcion").post("/turnos", json=TURNO)
        r2 = cliente_con_sesion(self.app, "admin").post("/turnos", json={**TURNO, "box_id": "BOX-2", "profesional_id": "PRO-002"})
        self.assertEqual((r1.status_code, r2.status_code), (201, 201))

    def test_permiso_se_evalua_antes_que_los_datos(self):
        cliente = cliente_con_sesion(self.app, "profesional")
        self.assertError(cliente.post("/turnos", content=b"{roto", headers={"content-type": "application/json"}), 403, "sin_permiso")


class CerrarSesion(BaseApi):
    def test_logout_revoca_el_token(self):
        token = iniciar_sesion(self.cliente)
        cabecera = {"Authorization": f"Bearer {token}"}
        self.assertEqual(self.cliente.post("/auth/logout", headers=cabecera).status_code, 204)
        self.assertError(self.cliente.get("/catalogo", headers=cabecera), 401, "token_invalido")
        self.assertError(self.cliente.post("/auth/logout", headers=cabecera), 401, "token_invalido")

    def test_logout_no_afecta_otras_sesiones(self):
        primera = iniciar_sesion(self.cliente)
        segunda = iniciar_sesion(self.cliente)
        self.cliente.post("/auth/logout", headers={"Authorization": f"Bearer {primera}"})
        self.assertEqual(self.cliente.get("/catalogo", headers={"Authorization": f"Bearer {segunda}"}).status_code, 200)


class Configuracion(unittest.TestCase):
    def test_secreto_corto_se_rechaza_al_iniciar(self):
        base = BaseDeDatosDePrueba()
        try:
            with self.assertRaises(ValueError):
                nueva_app(base, secreto_jwt="corto")
        finally:
            base.limpiar(crear_motor(base.url))

    def test_revocaciones_en_memoria_vencen(self):
        store = RevocacionesMemoria()
        store.revocar("a", time.time() + 60)
        store.revocar("b", time.time() - 1)
        self.assertTrue(store.esta_revocado("a"))
        self.assertFalse(store.esta_revocado("b"))
        self.assertFalse(store.esta_revocado("c"))


@unittest.skipUnless(os.environ.get("ODONTOLOGIA_TEST_REDIS_URL"), "Definir ODONTOLOGIA_TEST_REDIS_URL para probar contra Redis real")
class RevocacionesEnRedis(unittest.TestCase):
    def setUp(self):
        self.url = os.environ["ODONTOLOGIA_TEST_REDIS_URL"]
        self.store = RevocacionesRedis(self.url)

    def test_revocar_guarda_con_vencimiento(self):
        jti = uuid.uuid4().hex
        self.store.revocar(jti, time.time() + 120)
        self.assertTrue(self.store.esta_revocado(jti))
        ttl = self.store.cliente.ttl(f"odontologia:revocado:{jti}")
        self.assertTrue(0 < ttl <= 120)

    def test_token_ya_vencido_no_se_guarda(self):
        jti = uuid.uuid4().hex
        self.store.revocar(jti, time.time() - 5)
        self.assertFalse(self.store.esta_revocado(jti))

    def test_logout_por_api_usa_redis(self):
        base = BaseDeDatosDePrueba()
        app = nueva_app(base, redis_url=self.url)
        try:
            cliente = TestClient(app)
            token = iniciar_sesion(cliente)
            cliente.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
            jti = jwt.decode(token, SECRETO_PRUEBA, algorithms=["HS256"])["jti"]
            self.assertEqual(self.store.cliente.exists(f"odontologia:revocado:{jti}"), 1)
        finally:
            base.limpiar(app.state.motor)


if __name__ == "__main__":
    unittest.main()
