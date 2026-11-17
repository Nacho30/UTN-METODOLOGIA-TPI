# Design — C-02 consultar-agenda-diaria

## Context

C-01 dejó turnos guardados en UTC. Recepción piensa en "el día de hoy" en hora local. El change agrega lectura y la primera pantalla.

## Goals / Non-Goals

**Goals:** consulta diaria correcta en hora local, filtros, pantalla simple y probada.

**Non-Goals:** escribir datos desde la pantalla, autenticación, varias zonas horarias.

## Decisions

### D1 — Zona fija UTC-03:00
Argentina no aplica horario de verano, así que el consultorio usa un desfasaje fijo `-03:00` (`ZONA_CONSULTORIO`). El día consultado es `[00:00, 24:00)` local, convertido a UTC para la consulta. Si en el futuro hay sedes en otras zonas, se parametriza en un change nuevo.

### D2 — Intersección con el día, no "empieza ese día"
Se usa la misma fórmula de solapamiento de C-01: `turno.inicio < fin_del_dia` y `turno.fin > inicio_del_dia`. Un turno de 23:30 a 00:30 aparece en ambos días; si sólo se mirara el inicio, desaparecería del segundo día aunque ocupe el box.

### D3 — Orden `(inicio, id)`
Orden total y determinista: dos turnos a la misma hora siempre salen igual, lo que permite probarlo.

### D4 — Reutilizar validaciones de C-01
Los filtros usan el mismo validador de identificadores y el mismo formato de error. La fecha exige el patrón exacto `AAAA-MM-DD` porque `date.fromisoformat` de Python 3.11+ también acepta `20261201`.

### D5 — Frontend sin reglas de negocio
La pantalla sólo arma la URL, convierte UTC a hora local y muestra mensajes. Esa lógica vive en `src/agenda.ts` (funciones puras) y se prueba con `node:test` vía `tsx`, sin navegador. Vite reenvía `/api` al backend para evitar configurar CORS.

### D6 — Revisión con la skill propia
Antes de cerrar se revisó el change con `.agents/skills/odontologia-turnos` (intervalo `[inicio, fin)`, UTC, datos ficticios, reglas sólo en backend). Resultado registrado en `docs/evidencia/C-02-agenda-diaria.md`.

## Risks / Trade-offs

- **Zona fija:** si el país cambia su política horaria hay que actualizar la constante.
- **Sin paginación:** un consultorio pequeño tiene pocos turnos por día; se revisa si crece.
- **Pruebas de UI:** se prueban las funciones puras; el renderizado se verifica manualmente con `npm run dev`.
