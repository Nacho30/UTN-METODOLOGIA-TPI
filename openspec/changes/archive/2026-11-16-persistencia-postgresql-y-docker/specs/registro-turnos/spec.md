## MODIFIED Requirements

### Requirement: Altas simultáneas serializadas
La verificación de solapamientos y la inserción SHALL ejecutarse en la misma transacción. Con SQLite la transacción SHALL comenzar con `BEGIN IMMEDIATE`; con PostgreSQL SHALL bloquear con `SELECT … FOR UPDATE` la fila del profesional y luego la del box. En ambos casos dos altas simultáneas que compiten por el mismo recurso MUST NOT registrarse ambas.

#### Scenario: Dos altas al mismo tiempo
- **WHEN** dos conexiones independientes intentan registrar a la vez el mismo profesional en el mismo horario
- **THEN** una se registra, la otra recibe `conflicto_profesional` y la agenda tiene un solo turno

#### Scenario: Mismo box al mismo tiempo
- **WHEN** dos conexiones independientes intentan registrar a la vez el mismo box con distintos profesionales
- **THEN** una se registra y la otra recibe `conflicto_box`
