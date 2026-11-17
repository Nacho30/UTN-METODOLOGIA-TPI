import { useEffect, useState, type FormEvent } from "react";

import {
  construirUrlAgenda,
  hoyEnConsultorio,
  mensajeDeError,
  rangoHorario,
  type ErrorApi,
  type RespuestaAgenda,
} from "./agenda.ts";
import {
  borrarSesion,
  cabecerasCon,
  debeVolverAlLogin,
  guardarSesion,
  leerSesion,
  nombreRol,
  validarFormularioLogin,
  type Sesion,
} from "./sesion.ts";

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

class ErrorPeticion extends Error {
  constructor(public estado: number, mensaje: string) {
    super(mensaje);
  }
}

async function pedirJson<T>(url: string, token?: string, init: RequestInit = {}): Promise<T> {
  let respuesta: Response;
  try {
    respuesta = await fetch(url, {
      ...init,
      headers: { ...(token ? cabecerasCon(token) : {}), ...(init.headers as Record<string, string> | undefined) },
    });
  } catch {
    throw new ErrorPeticion(0, mensajeDeError(null));
  }
  const cuerpo = await respuesta.json().catch(() => null);
  if (!respuesta.ok) throw new ErrorPeticion(respuesta.status, mensajeDeError(cuerpo as ErrorApi | null));
  return cuerpo as T;
}

export default function App() {
  const [sesion, setSesion] = useState<Sesion | null>(() => leerSesion());
  const [aviso, setAviso] = useState("");

  const entrar = (nueva: Sesion) => {
    guardarSesion(nueva);
    setAviso("");
    setSesion(nueva);
  };

  const salir = (motivo = "") => {
    borrarSesion();
    setAviso(motivo);
    setSesion(null);
  };

  return sesion ? <Agenda sesion={sesion} onSalir={salir} /> : <Login aviso={aviso} onEntrar={entrar} />;
}

function Login({ aviso, onEntrar }: { aviso: string; onEntrar: (s: Sesion) => void }) {
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const [error, setError] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar(e: FormEvent) {
    e.preventDefault();
    const problema = validarFormularioLogin(usuario, clave);
    if (problema) return setError(problema);
    setEnviando(true);
    setError("");
    try {
      const r = await pedirJson<{ access_token: string; usuario: string; rol: string }>("/api/auth/login", undefined, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ usuario: usuario.trim(), clave }),
      });
      onEntrar({ token: r.access_token, usuario: r.usuario, rol: r.rol });
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login">
      <h1>Agenda del consultorio</h1>
      <p className="nota">Ingreso del personal — datos ficticios</p>
      {aviso && <p className="estado">{aviso}</p>}
      <form onSubmit={enviar}>
        <label>
          Usuario
          <input value={usuario} onChange={(e) => setUsuario(e.target.value)} autoComplete="username" />
        </label>
        <label>
          Clave
          <input type="password" value={clave} onChange={(e) => setClave(e.target.value)} autoComplete="current-password" />
        </label>
        {error && <p className="estado error" role="alert">{error}</p>}
        <button type="submit" disabled={enviando}>{enviando ? "Ingresando…" : "Ingresar"}</button>
      </form>
    </main>
  );
}

function Agenda({ sesion, onSalir }: { sesion: Sesion; onSalir: (motivo?: string) => void }) {
  const [fecha, setFecha] = useState(hoyEnConsultorio());
  const [profesionalId, setProfesionalId] = useState("");
  const [boxId, setBoxId] = useState("");
  const [catalogo, setCatalogo] = useState<Catalogo>({ profesionales: [], boxes: [] });
  const [estado, setEstado] = useState<Estado>({ tipo: "cargando" });

  const manejarError = (e: unknown) => {
    if (e instanceof ErrorPeticion && debeVolverAlLogin(e.estado)) {
      onSalir("Tu sesión venció o se cerró. Ingresá de nuevo.");
      return;
    }
    setEstado({ tipo: "error", mensaje: (e as Error).message });
  };

  useEffect(() => {
    pedirJson<Catalogo>("/api/catalogo", sesion.token).then(setCatalogo).catch(manejarError);
  }, [sesion.token]);

  useEffect(() => {
    if (!fecha) return;
    let vigente = true;
    setEstado({ tipo: "cargando" });
    pedirJson<RespuestaAgenda>(construirUrlAgenda(fecha, { profesionalId, boxId }), sesion.token)
      .then((agenda) => vigente && setEstado({ tipo: "listo", agenda }))
      .catch((e) => vigente && manejarError(e));
    return () => {
      vigente = false;
    };
  }, [fecha, profesionalId, boxId, sesion.token]);

  async function cerrarSesion() {
    await pedirJson("/api/auth/logout", sesion.token, { method: "POST" }).catch(() => undefined);
    onSalir();
  }

  return (
    <main>
      <header className="cabecera">
        <div>
          <h1>Agenda del día</h1>
          <p className="nota">Consultorio odontológico — datos ficticios · hora local UTC-03:00</p>
        </div>
        <div className="usuario">
          <span>{sesion.usuario} · {nombreRol(sesion.rol)}</span>
          <button type="button" onClick={cerrarSesion}>Salir</button>
        </div>
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
