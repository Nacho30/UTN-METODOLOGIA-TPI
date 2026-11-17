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

# Usuarios del personal (C-03). La clave NO está en el repositorio: se define en
# la variable de entorno ODONTOLOGIA_CLAVE_DEMO (o en .env con Docker) y al
# preparar la agenda se guarda sólo su hash PBKDF2. Sin esa variable no se crean.
USUARIOS = [
    ("recepcion", "Recepcionista Ficticia", "recepcion"),
    ("profesional", "Odontóloga Ficticia A", "profesional"),
    ("admin", "Administración Ficticia", "administracion"),
]
