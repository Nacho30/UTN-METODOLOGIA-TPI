# 05 — Funcionalidades

## US-01 — Registrar turno (C-01)
**Como** Recepción **quiero** registrar un turno indicando paciente, profesional, box y horario **para** no asignar dos veces el mismo profesional o box.

Criterios de aceptación:
- Turno válido y libre → 201 con el turno en UTC.
- Profesional ocupado → 409 `conflicto_profesional`; box ocupado → 409 `conflicto_box`.
- Turno pegado a otro → se registra.
- Datos inválidos → 422; recurso inexistente → 404. Nada se registra si hay error.
- Dos altas simultáneas para el mismo recurso → sólo una se registra.

## US-02 — Ver la agenda del día (C-02)
**Como** Recepción **quiero** ver los turnos de un día, opcionalmente por profesional o box, **para** organizar la atención.

Criterios de aceptación:
- Muestra sólo los turnos que ocupan ese día local, ordenados por hora.
- Un turno que cruza la medianoche aparece en los dos días.
- Fecha inválida → 422; filtro inexistente → 404; día sin turnos → lista vacía.
- La pantalla muestra horas locales y los estados cargando, vacío y error.

## Futuras
US-03 login (C-03), US-04 cancelar/reprogramar (C-04), US-05 pacientes (C-05), US-06 formulario de alta (C-06), US-07 recordatorios (C-08).
