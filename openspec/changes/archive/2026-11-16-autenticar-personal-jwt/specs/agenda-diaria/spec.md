## ADDED Requirements

### Requirement: Acceso con sesión
`GET /agenda` y `GET /catalogo` SHALL exigir una sesión válida con rol `recepcion`, `profesional` o `administracion` (ver `autenticacion-personal`). Sin sesión SHALL responder 401 `no_autenticado`.

#### Scenario: Profesional consulta la agenda
- **GIVEN** una sesión del usuario `profesional`
- **WHEN** consulta `GET /agenda?fecha=2026-12-01`
- **THEN** se responde 200

#### Scenario: Catálogo sin sesión
- **WHEN** se consulta `GET /catalogo` sin token
- **THEN** se responde 401 `no_autenticado`
