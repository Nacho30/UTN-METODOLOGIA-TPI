// Sesión del personal en el navegador (C-03).
// El backend decide los permisos; acá sólo se guarda el token y se arma la cabecera.

export interface Sesion {
  token: string;
  usuario: string;
  rol: string;
}

export interface Almacen {
  getItem(clave: string): string | null;
  setItem(clave: string, valor: string): void;
  removeItem(clave: string): void;
}

const CLAVE = "odontologia.sesion";

const ROLES: Record<string, string> = {
  recepcion: "Recepción",
  profesional: "Profesional",
  administracion: "Administración",
};

export function cabecerasCon(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` };
}

/** 401 = sesión ausente, vencida o cerrada: hay que volver a iniciar sesión. */
export function debeVolverAlLogin(estadoHttp: number): boolean {
  return estadoHttp === 401;
}

export function validarFormularioLogin(usuario: string, clave: string): string | null {
  if (!usuario.trim()) return "Ingresá el usuario.";
  if (!clave) return "Ingresá la clave.";
  return null;
}

export function nombreRol(rol: string): string {
  return ROLES[rol] ?? rol;
}

// sessionStorage: la sesión se borra al cerrar la pestaña. Si el navegador
// bloquea el almacenamiento, la app sigue funcionando sin recordar la sesión.
function almacenPorDefecto(): Almacen | null {
  try {
    return globalThis.sessionStorage ?? null;
  } catch {
    return null;
  }
}

export function guardarSesion(sesion: Sesion, almacen: Almacen | null = almacenPorDefecto()): void {
  try {
    almacen?.setItem(CLAVE, JSON.stringify(sesion));
  } catch {
    /* almacenamiento no disponible */
  }
}

export function leerSesion(almacen: Almacen | null = almacenPorDefecto()): Sesion | null {
  try {
    const crudo = almacen?.getItem(CLAVE);
    if (!crudo) return null;
    const dato = JSON.parse(crudo) as Partial<Sesion>;
    if (typeof dato.token === "string" && typeof dato.usuario === "string" && typeof dato.rol === "string") {
      return { token: dato.token, usuario: dato.usuario, rol: dato.rol };
    }
    return null;
  } catch {
    return null;
  }
}

export function borrarSesion(almacen: Almacen | null = almacenPorDefecto()): void {
  try {
    almacen?.removeItem(CLAVE);
  } catch {
    /* almacenamiento no disponible */
  }
}
