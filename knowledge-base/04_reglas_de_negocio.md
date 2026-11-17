# 04 — Reglas de negocio

| ID | Regla | Dónde se aplica | Prueba |
| --- | --- | --- | --- |
| RN-01 | Un profesional no puede tener turnos superpuestos | `servicio.registrar_turno` | `Solapamientos.test_conflicto_de_profesional_con_otro_box` |
| RN-02 | Un box no puede tener turnos superpuestos | `servicio.registrar_turno` | `Solapamientos.test_conflicto_de_box_con_otro_profesional` |
| RN-03 | Intervalo `[inicio, fin)`; turnos pegados permitidos | `_hay_solapamiento` | `Solapamientos.test_turnos_adyacentes_se_permiten` |
| RN-04 | Fecha-hora con zona horaria, minutos exactos, guardado en UTC; consultorio en UTC-03:00 | `_validar_instante`, `consultar_agenda` | `EntradasInvalidas.*`, `ServicioAgenda.*` |
| RN-05 | No hay sobreturnos | Consecuencia de RN-01/02 | — |
| RN-06 | Sólo datos ficticios | Catálogo y pruebas | Revisión con la skill propia |

## Superposición

Dos turnos A y B se superponen si `A.inicio < B.fin` **y** `A.fin > B.inicio`.

| Caso (turno existente 09:00–09:30) | Nuevo | ¿Choca? |
| --- | --- | --- |
| Igual | 09:00–09:30 | Sí |
| Empieza antes | 08:45–09:15 | Sí |
| Termina después | 09:15–09:45 | Sí |
| Contenido | 09:10–09:20 | Sí |
| Contiene | 08:30–10:00 | Sí |
| Pegado antes | 08:30–09:00 | No |
| Pegado después | 09:30–10:00 | No |

## Errores

| Código | HTTP | Cuándo |
| --- | --- | --- |
| `entrada_invalida` | 422 | Falta un campo, formato incorrecto, fecha sin zona, segundos, `inicio >= fin`, JSON inválido |
| `recurso_desconocido` | 404 | Paciente, profesional o box inexistente (se informa el primero, en ese orden) |
| `conflicto_profesional` | 409 | RN-01 (tiene prioridad si chocan ambos) |
| `conflicto_box` | 409 | RN-02 |

Formato de respuesta: `{"error": "...", "campo": "...", "mensaje": "..."}`.
