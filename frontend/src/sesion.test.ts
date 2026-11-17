// Pruebas de la sesión del personal (C-03). Ejecutar: npm test
import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import {
  borrarSesion,
  cabecerasCon,
  debeVolverAlLogin,
  leerSesion,
  nombreRol,
  validarFormularioLogin,
  guardarSesion,
} from "./sesion.ts";

class AlmacenFalso {
  datos = new Map<string, string>();
  getItem(k: string) { return this.datos.get(k) ?? null; }
  setItem(k: string, v: string) { this.datos.set(k, v); }
  removeItem(k: string) { this.datos.delete(k); }
}

const SESION = { token: "abc.def.ghi", usuario: "recepcion", rol: "recepcion" };

describe("cabecerasCon", () => {
  it("agrega el token como Bearer", () => {
    assert.deepEqual(cabecerasCon("abc"), { Authorization: "Bearer abc" });
  });
});

describe("debeVolverAlLogin", () => {
  it("sólo con 401 se vuelve al login", () => {
    assert.equal(debeVolverAlLogin(401), true);
    assert.equal(debeVolverAlLogin(403), false);
    assert.equal(debeVolverAlLogin(200), false);
  });
});

describe("validarFormularioLogin", () => {
  it("pide usuario y clave antes de llamar a la API", () => {
    assert.equal(validarFormularioLogin("", "x"), "Ingresá el usuario.");
    assert.equal(validarFormularioLogin("recepcion", ""), "Ingresá la clave.");
    assert.equal(validarFormularioLogin("recepcion", "x"), null);
  });
});

describe("nombreRol", () => {
  it("muestra nombres legibles", () => {
    assert.equal(nombreRol("recepcion"), "Recepción");
    assert.equal(nombreRol("administracion"), "Administración");
    assert.equal(nombreRol("otro"), "otro");
  });
});

describe("guardar y leer la sesión", () => {
  it("guarda y recupera la sesión", () => {
    const almacen = new AlmacenFalso();
    guardarSesion(SESION, almacen);
    assert.deepEqual(leerSesion(almacen), SESION);
    borrarSesion(almacen);
    assert.equal(leerSesion(almacen), null);
  });

  it("ignora datos rotos o incompletos", () => {
    const almacen = new AlmacenFalso();
    almacen.setItem("odontologia.sesion", "{roto");
    assert.equal(leerSesion(almacen), null);
    almacen.setItem("odontologia.sesion", JSON.stringify({ token: "x" }));
    assert.equal(leerSesion(almacen), null);
  });

  it("no falla si el navegador bloquea el almacenamiento", () => {
    const bloqueado = {
      getItem() { throw new Error("bloqueado"); },
      setItem() { throw new Error("bloqueado"); },
      removeItem() { throw new Error("bloqueado"); },
    };
    assert.equal(leerSesion(bloqueado), null);
    assert.doesNotThrow(() => guardarSesion(SESION, bloqueado));
    assert.doesNotThrow(() => borrarSesion(bloqueado));
  });
});
