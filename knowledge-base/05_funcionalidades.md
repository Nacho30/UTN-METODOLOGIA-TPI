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

## US-03 — Ingresar con mi usuario (C-03)
**Como** integrante del personal **quiero** ingresar con usuario y clave **para** que sólo el personal autorizado use la agenda.

Criterios de aceptación:
- Usuario y clave correctos → token JWT; incorrectos → 401 con el mismo mensaje.
- Sin sesión, toda operación de agenda responde 401.
- Profesional puede ver la agenda pero no registrar turnos (403).
- Al salir, el token deja de servir aunque no haya vencido.
- La pantalla pide ingresar antes de mostrar la agenda y vuelve al ingreso si la sesión vence.

## US-04 — Operar con PostgreSQL y Docker (C-04)
**Como** responsable técnico **quiero** correr el sistema con PostgreSQL y Docker Compose **para** usar el stack de producción indicado sin perder las garantías.

Criterios de aceptación:
- Toda la suite de pruebas pasa contra PostgreSQL.
- Dos altas simultáneas del mismo profesional o box: sólo una se registra.
- `docker compose up` levanta PostgreSQL, Redis, backend y frontend; los secretos van en `.env`.

## Futuras
US-05 cancelar/reprogramar (C-05), US-06 pacientes (C-06), US-07 formulario de alta (C-07), US-08 recordatorios (C-08).
