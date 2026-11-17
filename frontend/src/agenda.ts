// Lógica pura de la pantalla "Agenda del día" (C-02).
// No tiene reglas de negocio: sólo arma la consulta y da formato a lo que
// devuelve el backend. Se prueba con `npm test`.

export interface TurnoAgenda {
  id: number;
  paciente_id: string;
  profesional_id: string;
  box_id: string;
  inicio: string; // ISO 8601 en UTC, ej. "2026-12-01T12:00:00Z"
  fin: string;
  paciente_nombre: string;
  profesional_nombre: string;
  box_nombre: string;
}

export interface RespuestaAgenda {
  fecha: string;
  zona_horaria: string;
  turnos: TurnoAgenda[];
}

export interface ErrorApi {
  error: string;
  campo: string | null;
  mensaje: string;
}

export interface Filtros {
  profesionalId?: string;
  boxId?: string;
}

/** Desfasaje fijo del consultorio respecto de UTC, en minutos (UTC-03:00). */
export const DESFASAJE_CONSULTORIO_MIN = -3 * 60;

export function construirUrlAgenda(fecha: string, filtros: Filtros = {}, base = "/api"): string {
  const params = new URLSearchParams({ fecha });
  if (filtros.profesionalId) params.set("profesional_id", filtros.profesionalId);
  if (filtros.boxId) params.set("box_id", filtros.boxId);
  return `${base}/agenda?${params.toString()}`;
}

function aHoraConsultorio(isoUtc: string): Date {
  const instante = new Date(isoUtc);
  if (Number.isNaN(instante.getTime())) {
    throw new Error(`Fecha inválida recibida del backend: ${isoUtc}`);
  }
  return new Date(instante.getTime() + DESFASAJE_CONSULTORIO_MIN * 60_000);
}

const dosDigitos = (n: number) => String(n).padStart(2, "0");

/** "2026-12-01T12:00:00Z" → "09:00" (hora del consultorio). */
export function horaLocal(isoUtc: string): string {
  const local = aHoraConsultorio(isoUtc);
  return `${dosDigitos(local.getUTCHours())}:${dosDigitos(local.getUTCMinutes())}`;
}

/** Fecha local AAAA-MM-DD de un instante UTC. */
export function fechaLocal(isoUtc: string): string {
  const local = aHoraConsultorio(isoUtc);
  return `${local.getUTCFullYear()}-${dosDigitos(local.getUTCMonth() + 1)}-${dosDigitos(local.getUTCDate())}`;
}

/** Texto de horario; si el turno empieza o termina otro día lo aclara. */
export function rangoHorario(turno: Pick<TurnoAgenda, "inicio" | "fin">, fechaConsultada: string): string {
  const marca = (iso: string) => (fechaLocal(iso) === fechaConsultada ? "" : ` (${fechaLocal(iso).slice(8, 10)}/${fechaLocal(iso).slice(5, 7)})`);
  return `${horaLocal(turno.inicio)}${marca(turno.inicio)} – ${horaLocal(turno.fin)}${marca(turno.fin)}`;
}

/** Hoy en el consultorio, en formato AAAA-MM-DD. */
export function hoyEnConsultorio(ahora: Date = new Date()): string {
  return fechaLocal(ahora.toISOString());
}

const MENSAJES: Record<string, string> = {
  entrada_invalida: "Revisá los datos ingresados.",
  recurso_desconocido: "El profesional o box elegido no existe.",
};

/** Mensaje para mostrar a Recepción a partir del error del backend. */
export function mensajeDeError(error: Partial<ErrorApi> | null | undefined): string {
  if (!error || !error.error) return "No se pudo consultar la agenda. ¿Está corriendo el backend?";
  return error.mensaje || MENSAJES[error.error] || "Ocurrió un error inesperado.";
}
