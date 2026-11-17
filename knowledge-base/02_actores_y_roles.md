# 02 — Actores y roles

| Actor | Usuario ficticio | Rol | Necesita |
| --- | --- | --- | --- |
| Recepción | `recepcion` | `recepcion` | Dar turnos y ver la agenda |
| Profesional | `profesional` | `profesional` | Ver la agenda |
| Administración | `admin` | `administracion` | Todo lo anterior y, a futuro, mantener catálogo y usuarios |
| Paciente | — | — | No usa el sistema; sólo aparece como dato ficticio |

La clave de los tres usuarios ficticios se define fuera del repositorio, en `ODONTOLOGIA_CLAVE_DEMO` (variable de entorno o `.env`); en la base sólo queda su hash.

## Matriz de permisos (C-03, resuelve Q04)

| Operación | Ruta | recepcion | profesional | administracion |
| --- | --- | --- | --- | --- |
| Registrar turno | `POST /turnos` | ✅ | ❌ 403 | ✅ |
| Consultar agenda | `GET /agenda` | ✅ | ✅ | ✅ |
| Ver catálogo | `GET /catalogo` | ✅ | ✅ | ✅ |
| Ver mi usuario / salir | `GET /auth/yo`, `POST /auth/logout` | ✅ | ✅ | ✅ |
| Estado del servicio | `GET /health` | Público | Público | Público |

Los permisos se aplican **sólo en el backend** (`autenticacion.PERMISOS`). El frontend no decide nada.
