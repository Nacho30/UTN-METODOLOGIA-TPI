## ADDED Requirements

### Requirement: Catálogo ficticio preparado
El sistema SHALL preparar al iniciar una agenda con dos pacientes (`PAC-001`, `PAC-002`), dos profesionales (`PRO-001`, `PRO-002`) y dos boxes (`BOX-1`, `BOX-2`) ficticios. La preparación SHALL ser repetible y MUST NOT borrar turnos existentes.

#### Scenario: Agenda nueva
- **WHEN** se inicia el sistema con una base vacía
- **THEN** existen los seis recursos ficticios y ningún turno

#### Scenario: Reinicio con turnos cargados
- **GIVEN** una agenda con turnos registrados
- **WHEN** se vuelve a iniciar el sistema
- **THEN** los turnos se conservan y el catálogo no se duplica

### Requirement: Validación de identificadores
El sistema SHALL exigir `paciente_id`, `profesional_id` y `box_id` como textos no vacíos de hasta 64 caracteres, sin espacios al inicio o al final, y SHALL rechazar cualquier otro valor con `entrada_invalida` indicando el campo. Los valores MUST NOT corregirse silenciosamente.

#### Scenario: Campo faltante
- **WHEN** se solicita un alta sin `box_id`
- **THEN** se responde `entrada_invalida` con campo `box_id` y no se registra el turno

#### Scenario: Identificador mal formado
- **WHEN** `paciente_id` es vacío, numérico, tiene espacios extremos o supera 64 caracteres
- **THEN** se responde `entrada_invalida` con campo `paciente_id`

### Requirement: Recursos existentes
El sistema SHALL verificar que paciente, profesional y box existan en el catálogo, en ese orden, y SHALL rechazar el primero que falte con `recurso_desconocido` (HTTP 404) indicando el campo.

#### Scenario: Box inexistente
- **WHEN** se solicita un alta con `box_id` `BOX-9`
- **THEN** se responde 404 `recurso_desconocido` con campo `box_id`

#### Scenario: Varios recursos inexistentes
- **WHEN** paciente y profesional no existen
- **THEN** se informa sólo el paciente, porque se evalúa primero

### Requirement: Fechas con zona horaria y precisión de minutos
El sistema SHALL aceptar `inicio` y `fin` como fecha-hora ISO 8601 con zona horaria explícita (`-03:00`, `+00:00` o `Z`), con segundos y fracciones en cero, y con `inicio` anterior a `fin`. SHALL guardar y devolver los instantes en UTC. Cualquier otro valor SHALL rechazarse con `entrada_invalida` (HTTP 422) sin redondear.

#### Scenario: Conversión a UTC
- **WHEN** se registra un turno de 09:00 a 09:30 con zona `-03:00`
- **THEN** la respuesta 201 informa `inicio` `…T12:00:00Z` y `fin` `…T12:30:00Z`

#### Scenario: Fecha sin zona horaria
- **WHEN** `inicio` es `2026-12-01T09:00:00`
- **THEN** se responde 422 `entrada_invalida` con campo `inicio`

#### Scenario: Intervalo vacío o invertido
- **WHEN** `fin` es igual o anterior a `inicio`
- **THEN** se responde 422 `entrada_invalida` con campo `fin`

#### Scenario: Segundos distintos de cero
- **WHEN** `inicio` tiene 30 segundos
- **THEN** se responde 422 `entrada_invalida` con campo `inicio`

### Requirement: Sin solapamiento de profesional ni de box
Cada turno SHALL ocupar el intervalo semiabierto `[inicio, fin)`. El sistema MUST rechazar un alta cuyo intervalo se superponga con otro turno del mismo profesional (`conflicto_profesional`) o del mismo box (`conflicto_box`), ambos con HTTP 409. Si chocan los dos, SHALL informar primero el profesional. Los turnos adyacentes (uno termina cuando empieza el otro) SHALL permitirse. Un rechazo MUST NOT modificar la agenda.

#### Scenario: Mismo profesional en otro box
- **GIVEN** `PRO-001` tiene turno de 09:00 a 09:30 en `BOX-1`
- **WHEN** se pide `PRO-001` de 09:15 a 09:45 en `BOX-2`
- **THEN** se responde 409 `conflicto_profesional` y la agenda conserva sólo el turno original

#### Scenario: Mismo box con otro profesional
- **GIVEN** `BOX-1` ocupado de 09:00 a 09:30
- **WHEN** se pide `PRO-002` en `BOX-1` de 09:10 a 09:20
- **THEN** se responde 409 `conflicto_box`

#### Scenario: Choque de ambos recursos
- **WHEN** el nuevo turno repite profesional y box de un turno superpuesto
- **THEN** se responde `conflicto_profesional`

#### Scenario: Turnos adyacentes
- **GIVEN** `PRO-001` en `BOX-1` de 09:00 a 09:30
- **WHEN** se pide el mismo profesional y box de 09:30 a 10:00
- **THEN** se registra el turno con 201

#### Scenario: Offsets equivalentes
- **GIVEN** un turno de 09:00 a 09:30 `-03:00`
- **WHEN** se pide el mismo profesional de 12:00 a 12:30 `Z`
- **THEN** se detecta `conflicto_profesional`, porque es el mismo instante

### Requirement: Altas simultáneas serializadas
La verificación de solapamientos y la inserción SHALL ejecutarse en la misma transacción. Con SQLite la transacción SHALL comenzar con `BEGIN IMMEDIATE`, de modo que dos altas simultáneas que compiten por el mismo recurso no puedan registrarse ambas.

#### Scenario: Dos altas al mismo tiempo
- **WHEN** dos conexiones independientes intentan registrar a la vez el mismo profesional en el mismo horario
- **THEN** una se registra, la otra recibe `conflicto_profesional` y la agenda tiene un solo turno

### Requirement: Contrato HTTP
La API SHALL exponer `POST /turnos` y `GET /health`. Todo error SHALL responder un JSON `{error, campo, mensaje}`; un cuerpo que no sea JSON u objeto SHALL responder 422 `entrada_invalida`.

#### Scenario: JSON mal formado
- **WHEN** el cuerpo de `POST /turnos` no es JSON válido
- **THEN** se responde 422 `{"error": "entrada_invalida", "campo": null, …}`

#### Scenario: Salud del servicio
- **WHEN** se consulta `GET /health`
- **THEN** se responde 200 `{"estado": "ok"}`
