## MODIFIED Requirements

### Requirement: Contrato HTTP
La API SHALL exponer `POST /turnos` y `GET /health`. `POST /turnos` SHALL exigir una sesión válida con rol `recepcion` o `administracion` (ver `autenticacion-personal`); el permiso SHALL evaluarse antes de leer el cuerpo. Todo error SHALL responder un JSON `{error, campo, mensaje}`; un cuerpo que no sea JSON u objeto SHALL responder 422 `entrada_invalida`.

#### Scenario: JSON mal formado
- **GIVEN** una sesión de `recepcion`
- **WHEN** el cuerpo de `POST /turnos` no es JSON válido
- **THEN** se responde 422 `{"error": "entrada_invalida", "campo": null, …}`

#### Scenario: Sin sesión
- **WHEN** se hace `POST /turnos` sin token
- **THEN** se responde 401 `no_autenticado` y no se registra nada

#### Scenario: Salud del servicio
- **WHEN** se consulta `GET /health`
- **THEN** se responde 200 `{"estado": "ok"}`
