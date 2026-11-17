"""C-03 — Autenticación del personal con JWT y cierre de sesión con Redis.

Reglas:
- Las claves se guardan con PBKDF2-SHA256 y sal aleatoria; nunca en texto plano.
- El token es un JWT HS256 con sub, rol, jti, iat y exp (30 minutos por defecto).
- Cerrar sesión revoca el jti hasta su vencimiento. Con REDIS_URL se guarda en
  Redis; sin Redis, en memoria del proceso (sólo para desarrollo y pruebas).
- PERMISOS define qué rol puede hacer cada operación.
"""

import hashlib
import hmac
import math
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone

import jwt

from .errores import ErrorTurno

ALGORITMO = "HS256"
ITERACIONES = 260_000
LARGO_MINIMO_SECRETO = 32
MINUTOS_TOKEN = 30
ROLES = {"recepcion", "profesional", "administracion"}

PERMISOS = {
    "registrar_turno": {"recepcion", "administracion"},
    "consultar_agenda": {"recepcion", "profesional", "administracion"},
}


# ---------------------------------------------------------------- claves

def hashear_clave(clave: str, sal: bytes | None = None) -> str:
    sal = sal or secrets.token_bytes(16)
    resumen = hashlib.pbkdf2_hmac("sha256", clave.encode(), sal, ITERACIONES)
    return f"pbkdf2_sha256${ITERACIONES}${sal.hex()}${resumen.hex()}"


def verificar_clave(clave: str, guardado: str) -> bool:
    try:
        esquema, iteraciones, sal, resumen = guardado.split("$")
        if esquema != "pbkdf2_sha256":
            return False
        calculado = hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), int(iteraciones))
    except ValueError:
        return False
    return hmac.compare_digest(calculado.hex(), resumen)


# ---------------------------------------------------------------- tokens

LARGO_MINIMO_CLAVE_DEMO = 8


def validar_clave_demo(clave: str | None) -> str | None:
    if clave is not None and len(clave) < LARGO_MINIMO_CLAVE_DEMO:
        raise ValueError(f"ODONTOLOGIA_CLAVE_DEMO debe tener al menos {LARGO_MINIMO_CLAVE_DEMO} caracteres.")
    return clave


def validar_secreto(secreto: str) -> str:
    if not isinstance(secreto, str) or len(secreto) < LARGO_MINIMO_SECRETO:
        raise ValueError(f"El secreto JWT debe tener al menos {LARGO_MINIMO_SECRETO} caracteres.")
    return secreto


def emitir_token(usuario: str, rol: str, secreto: str, minutos: int = MINUTOS_TOKEN) -> str:
    ahora = datetime.now(timezone.utc)
    datos = {
        "sub": usuario,
        "rol": rol,
        "jti": uuid.uuid4().hex,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=minutos),
    }
    return jwt.encode(datos, secreto, algorithm=ALGORITMO)


def _token_invalido() -> ErrorTurno:
    return ErrorTurno("token_invalido", None, "La sesión no es válida o venció. Iniciá sesión de nuevo.")


def leer_token(token: str, secreto: str, revocaciones) -> dict:
    """Valida firma, vencimiento, campos obligatorios, rol y revocación."""
    try:
        datos = jwt.decode(
            token, secreto, algorithms=[ALGORITMO],
            options={"require": ["sub", "rol", "jti", "exp"]},
        )
    except jwt.PyJWTError:
        raise _token_invalido() from None
    if datos["rol"] not in ROLES or not isinstance(datos["jti"], str) or revocaciones.esta_revocado(datos["jti"]):
        raise _token_invalido()
    return datos


def exigir_permiso(datos_token: dict, operacion: str) -> None:
    if datos_token["rol"] not in PERMISOS[operacion]:
        raise ErrorTurno("sin_permiso", None, "Tu rol no tiene permiso para esta operación.")


# ---------------------------------------------------------------- login

def validar_login(datos) -> tuple[str, str]:
    if not isinstance(datos, dict):
        raise ErrorTurno("entrada_invalida", None, "El cuerpo debe ser un objeto JSON.")
    for campo in ("usuario", "clave"):
        valor = datos.get(campo)
        if not isinstance(valor, str) or not valor:
            raise ErrorTurno("entrada_invalida", campo, f"{campo} es obligatorio y debe ser texto.")
    return datos["usuario"], datos["clave"]


def credenciales_invalidas() -> ErrorTurno:
    # Mismo mensaje para usuario inexistente y clave incorrecta: no revela qué usuarios existen.
    return ErrorTurno("credenciales_invalidas", None, "Usuario o clave incorrectos.")


# ---------------------------------------------------------------- revocaciones

class RevocacionesMemoria:
    """Lista de tokens cerrados en memoria. Se pierde al reiniciar el proceso."""

    def __init__(self):
        self._vencimientos: dict[str, float] = {}

    def revocar(self, jti: str, vence_en: float) -> None:
        if vence_en > time.time():
            self._vencimientos[jti] = vence_en

    def esta_revocado(self, jti: str) -> bool:
        vence = self._vencimientos.get(jti)
        if vence is None:
            return False
        if vence <= time.time():
            del self._vencimientos[jti]
            return False
        return True


class RevocacionesRedis:
    """Lista de tokens cerrados en Redis, con TTL igual al tiempo que le queda al token."""

    PREFIJO = "odontologia:revocado:"

    def __init__(self, url: str):
        import redis  # import diferido: Redis es opcional en desarrollo

        self.cliente = redis.Redis.from_url(url)

    def revocar(self, jti: str, vence_en: float) -> None:
        segundos = math.ceil(vence_en - time.time())
        if segundos > 0:
            self.cliente.set(self.PREFIJO + jti, 1, ex=segundos)

    def esta_revocado(self, jti: str) -> bool:
        return bool(self.cliente.exists(self.PREFIJO + jti))


def crear_revocaciones(redis_url: str | None):
    return RevocacionesRedis(redis_url) if redis_url else RevocacionesMemoria()
