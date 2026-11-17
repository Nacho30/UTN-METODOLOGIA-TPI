import { useEffect, useState } from "react";

import {
  construirUrlAgenda,
  hoyEnConsultorio,
  mensajeDeError,
  rangoHorario,
  type ErrorApi,
  type RespuestaAgenda,
} from "./agenda.ts";

interface Opcion {
  id: string;
  nombre: string;
}

interface Catalogo {
  profesionales: Opcion[];
  boxes: Opcion[];
}

type Estado =
  | { tipo: "cargando" }
  | { tipo: "error"; mensaje: string }
  | { tipo: "listo"; agenda: RespuestaAgenda };

async function pedirJson<T>(url: string): Promise<T> {
  let respuesta: Response;
  try {
    respuesta = await fetch(url);
  } catch {
    throw new Error(mensajeDeError(null));
  }
  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) throw new Error(mensajeDeError(cuerpo as ErrorApi | null));
  return cuerpo as T;
}

export default function App() {
  const [fecha, setFecha] = useState(hoyEnConsultorio());
  const [profesionalId, setProfesionalId] = useState("");
  const [boxId, setBoxId] = useState("");
  const [catalogo, setCatalogo] = useState<Catalogo>({ profesionales: [], boxes: [] });
  const [estado, setEstado] = useState<Estado>({ tipo: "cargando" });

  useEffect(() => {
    pedirJson<Catalogo>("/api/catalogo").then(setCatalogo).catch(() => undefined);
  }, []);

  useEffect(() => {
    if (!fecha) return;
    let vigente = true;
    setEstado({ tipo: "cargando" });
    pedirJson<RespuestaAgenda>(construirUrlAgenda(fecha, { profesionalId, boxId }))
      .then((agenda) => vigente && setEstado({ tipo: "listo", agenda }))
      .catch((e: Error) => vigente && setEstado({ tipo: "error", mensaje: e.message }));
    return () => {
      vigente = false;
    };
  }, [fecha, profesionalId, boxId]);

  return (
    <main>
      <header>
        <h1>Agenda del día</h1>
        <p className="nota">Consultorio odontológico — datos ficticios · hora local UTC-03:00</p>
      </header>

      <section className="filtros" aria-label="Filtros">
        <label>
          Fecha
          <input type="date" value={fecha} onChange={(e) => setFecha(e.target.value)} required />
        </label>
        <label>
          Profesional
          <select value={profesionalId} onChange={(e) => setProfesionalId(e.target.value)}>
            <option value="">Todos</option>
            {catalogo.profesionales.map((p) => (
              <option key={p.id} value={p.id}>{p.nombre}</option>
            ))}
          </select>
        </label>
        <label>
          Box
          <select value={boxId} onChange={(e) => setBoxId(e.target.value)}>
            <option value="">Todos</option>
            {catalogo.boxes.map((b) => (
              <option key={b.id} value={b.id}>{b.nombre}</option>
            ))}
          </select>
        </label>
      </section>

      {estado.tipo === "cargando" && <p className="estado">Cargando agenda…</p>}
      {estado.tipo === "error" && <p className="estado error" role="alert">{estado.mensaje}</p>}
      {estado.tipo === "listo" && estado.agenda.turnos.length === 0 && (
        <p className="estado">No hay turnos para esta fecha.</p>
      )}
      {estado.tipo === "listo" && estado.agenda.turnos.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Horario</th>
              <th>Paciente</th>
              <th>Profesional</th>
              <th>Box</th>
            </tr>
          </thead>
          <tbody>
            {estado.agenda.turnos.map((t) => (
              <tr key={t.id}>
                <td>{rangoHorario(t, estado.agenda.fecha)}</td>
                <td>{t.paciente_nombre}</td>
                <td>{t.profesional_nombre}</td>
                <td>{t.box_nombre}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
