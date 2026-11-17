"""Catálogo FICTICIO para la demo y las pruebas. No contiene personas reales."""

PACIENTES = [
    ("PAC-001", "Paciente Ficticio Uno"),
    ("PAC-002", "Paciente Ficticio Dos"),
]

PROFESIONALES = [
    ("PRO-001", "Odontóloga Ficticia A"),
    ("PRO-002", "Odontólogo Ficticio B"),
]

BOXES = [
    ("BOX-1", "Box 1"),
    ("BOX-2", "Box 2"),
]

# Usuarios del personal (C-03). La clave de demostración es la MISMA para los
# tres y es pública a propósito: sólo sirve para probar el sistema local con
# datos ficticios. Se guarda únicamente su hash PBKDF2.
CLAVE_DEMO = "Clave-Demo-2026"
_HASH_CLAVE_DEMO = (
    "pbkdf2_sha256$260000$20c1f4273662f830d84d7bfe161afc2f$"
    "6eadf3839e9cad8aef7aff20c432a8d066dc960c540c9fb21c00fa5da92486c7"
)

USUARIOS = [
    ("recepcion", "Recepcionista Ficticia", "recepcion", _HASH_CLAVE_DEMO),
    ("profesional", "Odontóloga Ficticia A", "profesional", _HASH_CLAVE_DEMO),
    ("admin", "Administración Ficticia", "administracion", _HASH_CLAVE_DEMO),
]
