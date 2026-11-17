// Pruebas de la lógica de la agenda (C-02). Ejecutar: npm test
import { strict as assert } from "node:assert";
import { describe, it } from "node:test";

import {
  construirUrlAgenda,
  fechaLocal,
  horaLocal,
  hoyEnConsultorio,
  mensajeDeError,
  rangoHorario,
} from "./agenda.ts";

describe("construirUrlAgenda", () => {
  it("arma la consulta sólo con la fecha", () => {
    assert.equal(construirUrlAgenda("2026-12-01"), "/api/agenda?fecha=2026-12-01");
  });

  it("agrega los filtros elegidos y omite los vacíos", () => {
    assert.equal(
      construirUrlAgenda("2026-12-01", { profesionalId: "PRO-001", boxId: "" }),
      "/api/agenda?fecha=2026-12-01&profesional_id=PRO-001",
    );
    assert.equal(
      construirUrlAgenda("2026-12-01", { profesionalId: "PRO-002", boxId: "BOX-1" }, "http://x"),
      "http://x/agenda?fecha=2026-12-01&profesional_id=PRO-002&box_id=BOX-1",
    );
  });
});

describe("hora del consultorio (UTC-03:00)", () => {
  it("convierte UTC a hora local", () => {
    assert.equal(horaLocal("2026-12-01T12:00:00Z"), "09:00");
    assert.equal(horaLocal("2026-12-01T02:30:00Z"), "23:30");
  });

  it("calcula la fecha local, aunque cambie el día", () => {
    assert.equal(fechaLocal("2026-12-01T12:00:00Z"), "2026-12-01");
    assert.equal(fechaLocal("2026-12-01T02:30:00Z"), "2026-11-30");
  });

  it("hoy en el consultorio usa la hora local y no la UTC", () => {
    assert.equal(hoyEnConsultorio(new Date("2026-12-02T01:00:00Z")), "2026-12-01");
    assert.equal(hoyEnConsultorio(new Date("2026-12-02T03:00:00Z")), "2026-12-02");
  });

  it("rechaza fechas inválidas en lugar de mostrar NaN", () => {
    assert.throws(() => horaLocal("no-es-fecha"), /Fecha inválida/);
  });
});

describe("rangoHorario", () => {
  it("muestra sólo horas si el turno es del día consultado", () => {
    assert.equal(
      rangoHorario({ inicio: "2026-12-01T12:00:00Z", fin: "2026-12-01T12:30:00Z" }, "2026-12-01"),
      "09:00 – 09:30",
    );
  });

  it("aclara el día cuando el turno cruza la medianoche", () => {
    const turno = { inicio: "2026-12-01T02:30:00Z", fin: "2026-12-01T03:30:00Z" };
    assert.equal(rangoHorario(turno, "2026-12-01"), "23:30 (30/11) – 00:30");
    assert.equal(rangoHorario(turno, "2026-11-30"), "23:30 – 00:30 (01/12)");
  });
});

describe("mensajeDeError", () => {
  it("usa el mensaje del backend cuando existe", () => {
    assert.equal(
      mensajeDeError({ error: "recurso_desconocido", campo: "box_id", mensaje: "No existe box_id 'BOX-9'." }),
      "No existe box_id 'BOX-9'.",
    );
  });

  it("tiene textos por defecto y para backend caído", () => {
    assert.equal(mensajeDeError({ error: "entrada_invalida" }), "Revisá los datos ingresados.");
    assert.equal(mensajeDeError({ error: "sin_permiso" }), "Tu rol no tiene permiso para esta operación.");
    assert.match(mensajeDeError(null), /backend/);
  });
});
