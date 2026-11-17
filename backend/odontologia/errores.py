"""Errores de negocio con código estable y estado HTTP asociado."""

ESTADO_HTTP = {
    "entrada_invalida": 422,
    "recurso_desconocido": 404,
    "conflicto_profesional": 409,
    "conflicto_box": 409,
}


class ErrorTurno(Exception):
    """Rechazo explícito de una operación de agenda.

    `codigo` es estable y lo consumen la API y el frontend; `campo` indica
    qué dato provocó el rechazo cuando corresponde.
    """

    def __init__(self, codigo: str, campo: str | None, mensaje: str):
        super().__init__(mensaje)
        self.codigo = codigo
        self.campo = campo
        self.mensaje = mensaje

    @property
    def estado_http(self) -> int:
        return ESTADO_HTTP[self.codigo]

    def como_dict(self) -> dict:
        return {"error": self.codigo, "campo": self.campo, "mensaje": self.mensaje}
