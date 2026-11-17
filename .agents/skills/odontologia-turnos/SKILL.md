---
name: odontologia-turnos
description: Revisa propuestas, specs, código y pruebas de la agenda odontológica de este repo contra sus invariantes de dominio (intervalo [inicio, fin), UTC, no solapamiento de profesional y box, concurrencia en SQLite y PostgreSQL, permisos JWT, datos ficticios y secretos fuera del repo). Usala siempre junto con las skills de OpenSpec al proponer, aplicar o archivar un change, y también cuando alguien pida revisar un diff, una spec o una prueba que toque turnos, agenda, profesionales, boxes, login o la base de datos, aunque no mencione esta skill.
---

# Revisión de dominio — agenda odontológica

Las skills de OpenSpec saben **cómo** escribir una propuesta, una spec o unas tareas, pero no conocen las reglas de esta agenda. Un detalle pequeño —un `<=` en lugar de `<`, una hora sin zona horaria, una regla puesta en el frontend— rompe el sistema sin que ninguna prueba genérica lo note. Esta skill es el control de dominio que se suma a OpenSpec: **no la reemplaza** y no escribe código ni artefactos; produce un informe de hallazgos.

## Cuándo usarla

- Al terminar `proposal.md` / `design.md` / `spec.md` de un change, antes de aplicar.
- Antes de marcar como hechas las tareas de Apply.
- Antes de archivar (el resultado se pega al final de `docs/evidencia/<change>.md`).
- Cuando se pide revisar un diff o una prueba que toque turnos, agenda, login o la base.

## Qué leer primero

1. `knowledge-base/04_reglas_de_negocio.md`: reglas RN y tabla de errores.
2. `knowledge-base/02_actores_y_roles.md`: matriz de permisos.
3. `knowledge-base/06_arquitectura.md`: capas, endpoints y configuración.
4. Las specs vigentes en `openspec/specs/` que toque el change.

Leerlos evita revisar contra la memoria del modelo en lugar de contra lo acordado.

## Checklist de invariantes

Responder cada punto con ✅, ❌ (con archivo y línea) o N/A, y en ❌ explicar la consecuencia concreta.

1. **Intervalo `[inicio, fin)`.** La superposición es `a.inicio < b.fin and a.fin > b.inicio`; los turnos pegados se permiten. *Por qué:* con `<=` un turno de 09:00–09:30 bloquearía otro de 09:30–10:00 y la agenda perdería huecos válidos.
2. **Zona horaria y UTC.** Las entradas exigen offset explícito; se compara y guarda en UTC; el día del consultorio es UTC-03:00; nada se redondea. *Por qué:* "09:00" sin zona puede ser dos instantes distintos y producir choques invisibles.
3. **No solapamiento por profesional y por box**, dentro de la misma transacción que el INSERT o UPDATE, informando primero el profesional. *Por qué:* si la verificación queda fuera de la transacción, otra alta puede colarse entre medio.
4. **Concurrencia.** SQLite: `BEGIN IMMEDIATE`. PostgreSQL: `SELECT … FOR UPDATE` de profesional y luego box (orden fijo, sin deadlocks). Un mecanismo nuevo se prueba con conexiones independientes y con RED previo. *Por qué:* una prueba secuencial pasa aunque haya carrera; en C-04 la carrera duplicó turnos en 9 de 10 rondas.
5. **Errores.** Sólo códigos declarados en la spec (`entrada_invalida` 422, `recurso_desconocido` 404, `conflicto_profesional`/`conflicto_box` 409, `credenciales_invalidas`/`no_autenticado`/`token_invalido` 401, `sin_permiso` 403), con formato `{error, campo, mensaje}`. Un rechazo no modifica datos. *Por qué:* el frontend y las pruebas dependen de esos códigos exactos.
6. **Capas.** Reglas en `backend/odontologia/servicio.py`, permisos en `autenticacion.py`; `api.py` sólo adapta; el frontend no decide. *Por qué:* una regla duplicada en la pantalla se puede saltear llamando a la API.
7. **Datos ficticios.** Sólo `PAC-*`, `PRO-*`, `BOX-*` y nombres "Ficticio". Ningún nombre, DNI, teléfono ni dato clínico real.
8. **Pruebas.** Cada escenario de la spec tiene al menos una prueba; hay evidencia RED antes de GREEN; la suite completa pasa en SQLite y, si toca la base, también con `ODONTOLOGIA_TEST_DB_URL` (PostgreSQL).
9. **Alcance.** Nada fuera del `proposal.md` del change; sin sobreturnos.
10. **Seguridad y secretos.** Toda ruta nueva exige sesión JWT salvo que la spec diga lo contrario. Ningún secreto en el repo: secreto JWT, clave de PostgreSQL y clave de demostración (`ODONTOLOGIA_CLAVE_DEMO`) sólo en `.env` o variables de entorno. *Por qué:* la consigna pide claves fuera del repositorio, de la entrega y del video.

## Formato de salida

Usar siempre esta plantilla, para que las revisiones de distintos changes se puedan comparar:

```markdown
## Revisión con la skill `odontologia-turnos` — <change>
| # | Invariante | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Intervalo `[inicio, fin)` | ✅ | servicio.py `_hay_solapamiento` |
| … | … | … | … |
**Bloqueantes:** <lista de ❌ o "ninguno">
```

Si hay un ❌, el change no se archiva hasta corregirlo y volver a revisar.

## Pruebas de la skill

`evals/` tiene casos para comprobar que la skill detecta errores típicos. Se pueden correr con `claude plugin eval .` desde esta carpeta (Claude Code) o a mano siguiendo `prompt.md`.
