# agenda-diaria Specification

## Purpose
Permitir que Recepción consulte los turnos de un día del consultorio, con filtros opcionales por profesional y box, desde la API y desde una pantalla web. Origen: change C-02 `consultar-agenda-diaria`; C-03 agregó el acceso con sesión.

## Requirements

### Requirement: Consulta por día local del consultorio
El sistema SHALL exponer `GET /agenda?fecha=AAAA-MM-DD` y devolver los turnos que ocupen parte del día local `[00:00, 24:00)` en la zona del consultorio (UTC-03:00 fija). La respuesta SHALL incluir `fecha`, `zona_horaria` (`-03:00`) y `turnos`, con instantes en UTC.

#### Scenario: Día con turnos
- **GIVEN** turnos el 01/12 y el 02/12
- **WHEN** se consulta `fecha=2026-12-01`
- **THEN** se devuelven sólo los turnos que ocupan el 01/12

#### Scenario: Turno que cruza la medianoche
- **GIVEN** un turno de 23:30 del 30/11 a 00:30 del 01/12 (hora local)
- **WHEN** se consulta el 30/11 o el 01/12
- **THEN** el turno aparece en ambos días

#### Scenario: Día sin turnos
- **WHEN** se consulta una fecha sin turnos
- **THEN** se responde 200 con `turnos` vacío

### Requirement: Orden estable
Los turnos SHALL ordenarse por `inicio` ascendente y, a igual inicio, por `id` ascendente.

#### Scenario: Dos turnos a la misma hora
- **GIVEN** dos turnos de distintos profesionales a las 09:00
- **WHEN** se consulta el día
- **THEN** aparecen ordenados por `id`

### Requirement: Filtros opcionales validados
El sistema SHALL aceptar `profesional_id` y `box_id` opcionales, combinables. Un filtro mal formado SHALL responder 422 `entrada_invalida` y uno inexistente 404 `recurso_desconocido`, ambos indicando el campo.

#### Scenario: Filtro por profesional
- **WHEN** se consulta con `profesional_id=PRO-002`
- **THEN** sólo se devuelven turnos de `PRO-002`

#### Scenario: Profesional inexistente
- **WHEN** se consulta con `profesional_id=PRO-999`
- **THEN** se responde 404 `recurso_desconocido` con campo `profesional_id`

### Requirement: Fecha obligatoria y válida
La `fecha` SHALL ser obligatoria, con formato exacto `AAAA-MM-DD` y existente en el calendario; en otro caso SHALL responder 422 `entrada_invalida` con campo `fecha`.

#### Scenario: Sin fecha
- **WHEN** se consulta `GET /agenda` sin parámetros
- **THEN** se responde 422 `entrada_invalida` con campo `fecha`

#### Scenario: Fecha inexistente o con otro formato
- **WHEN** `fecha` es `2026-02-30`, `01/12/2026` o `20261201`
- **THEN** se responde 422 `entrada_invalida` con campo `fecha`

### Requirement: Datos para mostrar
Cada turno de la agenda SHALL incluir, además de los identificadores, `paciente_nombre`, `profesional_nombre` y `box_nombre` del catálogo ficticio. El sistema SHALL exponer `GET /catalogo` con profesionales y boxes ordenados por `id` para poblar filtros.

#### Scenario: Catálogo para filtros
- **WHEN** se consulta `GET /catalogo`
- **THEN** se devuelven `PRO-001`, `PRO-002` y `BOX-1`, `BOX-2`

### Requirement: Pantalla "Agenda del día"
El frontend SHALL mostrar la agenda del día con selector de fecha (por defecto, hoy en el consultorio) y filtros de profesional y box. SHALL mostrar las horas en hora local, aclarar la fecha cuando un turno empieza o termina otro día, y distinguir los estados cargando, vacío y error. MUST NOT aplicar reglas de negocio: sólo consume la API.

#### Scenario: Conversión de hora
- **WHEN** la API devuelve `inicio` `2026-12-01T12:00:00Z`
- **THEN** la pantalla muestra `09:00`

#### Scenario: Backend apagado
- **WHEN** la API no responde
- **THEN** la pantalla muestra un mensaje de error que sugiere revisar el backend

### Requirement: Acceso con sesión
`GET /agenda` y `GET /catalogo` SHALL exigir una sesión válida con rol `recepcion`, `profesional` o `administracion` (ver `autenticacion-personal`). Sin sesión SHALL responder 401 `no_autenticado`.

#### Scenario: Profesional consulta la agenda
- **GIVEN** una sesión del usuario `profesional`
- **WHEN** consulta `GET /agenda?fecha=2026-12-01`
- **THEN** se responde 200

#### Scenario: Catálogo sin sesión
- **WHEN** se consulta `GET /catalogo` sin token
- **THEN** se responde 401 `no_autenticado`
