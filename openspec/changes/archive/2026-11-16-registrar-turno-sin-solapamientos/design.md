# Design — C-01 registrar-turno-sin-solapamientos

## Context

Primer change del sistema. El stack lo fijó la cátedra (Python, FastAPI, SQLAlchemy, React + TypeScript + Vite). El change sólo necesita backend.

## Goals / Non-Goals

**Goals:** alta de turnos correcta, validada, persistente y segura ante altas simultáneas; errores claros y estables para el frontend.

**Non-Goals:** autenticación, edición o baja de turnos, PostgreSQL, interfaz web.

## Decisions

### D1 — Capas: servicio con las reglas, API como adaptador
`servicio.registrar_turno(sesiones, datos)` contiene validación y reglas; `api.py` sólo traduce HTTP ↔ servicio. Así las reglas se prueban sin HTTP y la API no duplica lógica.
*Alternativa descartada:* validar con modelos Pydantic en el endpoint. Se descartó porque el formato de error de Pydantic no coincide con el contrato `{error, campo, mensaje}` y ataría la regla a la capa HTTP.

### D2 — Intervalo semiabierto `[inicio, fin)`
Dos turnos se solapan si `existente.inicio < nuevo.fin` y `existente.fin > nuevo.inicio`. Con esta fórmula un turno que termina 09:30 y otro que empieza 09:30 no chocan (adyacencia permitida), que es lo habitual en una agenda.

### D3 — Fechas con zona obligatoria, guardado en UTC
Se exige offset explícito para no adivinar la zona del cliente. Todo se compara y guarda en UTC (columna `DateTime` sin tzinfo, interpretada como UTC). Se exigen minutos exactos y no se redondea: un dato inválido se rechaza, no se corrige.

### D4 — Orden de evaluación y prioridad de errores
Forma de los datos → existencia (paciente, profesional, box) → conflicto de profesional → conflicto de box. Orden determinista, testeable y fácil de explicar a Recepción.

### D5 — Concurrencia con `BEGIN IMMEDIATE`
En SQLite, un `BEGIN` común toma el lock de escritura recién al insertar: dos altas podrían consultar a la vez, ver el horario libre y registrarse ambas. Con `BEGIN IMMEDIATE` (configurado en `db.crear_motor` mediante eventos de SQLAlchemy) la segunda transacción espera a que termine la primera y luego ve el turno ya registrado. Timeout de espera: 5 s.
*Evidencia:* con `BEGIN` común la prueba de concurrencia falló 4 de 5 veces; con `BEGIN IMMEDIATE`, 5 de 5 pasaron (ver `docs/evidencia/C-01-registrar-turno.md`).

### D6 — Catálogo ficticio sembrado al iniciar
`preparar_agenda` crea tablas y agrega los recursos faltantes sin borrar turnos. Los nombres son explícitamente ficticios (R-02).

## Risks / Trade-offs

- **SQLite y un solo equipo:** la garantía no cubre varias máquinas ni escrituras externas → C-07 migra a PostgreSQL con su propio mecanismo de bloqueo.
- **Endpoint `async` con acceso síncrono a la base:** serializa peticiones en el proceso; aceptable para una API local de demostración.
- **Sin idempotencia:** repetir la misma solicitud da `conflicto_profesional`, no el turno anterior.
