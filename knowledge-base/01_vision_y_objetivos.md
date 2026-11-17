# 01 — Visión y objetivos

## Visión
Que Recepción de un consultorio odontológico pequeño pueda dar turnos **sin dobles reservas** y ver la agenda del día en segundos, con acceso sólo para el personal autorizado.

## Objetivos de esta entrega (TPI)
1. **C-01:** registrar turnos rechazando choques de profesional y de box (D-01).
2. **C-02:** consultar la agenda de un día por API y por pantalla web (D-02).
3. **C-03:** login del personal con JWT, permisos por rol y cierre de sesión con Redis (D-03).
4. **C-04:** correr sobre PostgreSQL sin perder la garantía de no solapamiento y levantar todo con Docker Compose.
5. Usar el **stack completo** indicado por la cátedra.
6. Demostrar el flujo **Discovery → KB → Roadmap → OpenSpec → pruebas** con un agente de IA, una skill propia y un MCP.

## Indicadores de éxito
- 0 turnos superpuestos para el mismo profesional o box, incluso con altas simultáneas, en SQLite y en PostgreSQL.
- Ninguna operación de agenda sin sesión válida.
- Todas las reglas cubiertas por pruebas automáticas.
- El proyecto se levanta siguiendo sólo el README (con o sin Docker).

## Límites
Sólo datos ficticios, API local, sin integraciones externas ni historia clínica.
