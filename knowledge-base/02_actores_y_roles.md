# 02 — Actores y roles

| Actor | Necesita | En C-01 / C-02 | Futuro |
| --- | --- | --- | --- |
| Recepción | Dar turnos y ver la agenda | Usa `POST /turnos`, `GET /agenda` y la pantalla | Login (C-03), cancelar/reprogramar (C-04), formulario (C-06) |
| Profesional | Ver su agenda | Puede filtrar la agenda por profesional | Ver sólo la suya (C-03) |
| Administración | Mantener catálogo y usuarios | — (catálogo ficticio fijo) | C-03, C-05 |
| Paciente | Asistir al turno | Sólo aparece como dato ficticio | Recordatorios simulados (C-08) |

En esta entrega **no hay autenticación**: la API es local (127.0.0.1) y de demostración. La matriz de permisos se decide en C-03.
