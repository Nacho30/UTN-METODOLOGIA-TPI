---
name: odontologia-turnos
description: Revisa propuestas, specs, código y pruebas de la agenda odontológica de este repo contra sus invariantes de dominio (intervalo [inicio, fin), UTC, no solapamiento de profesional y box, datos ficticios, reglas sólo en backend). Usar junto con las skills de OpenSpec al proponer, aplicar o archivar cualquier change que toque turnos o agenda.
---

# Revisión de dominio — agenda odontológica

Esta skill **no reemplaza** a las skills de OpenSpec (`openspec-propose`, `openspec-apply-change`, `openspec-archive-change`). Se usa junto con ellas para no romper las reglas del dominio. No crea código ni artefactos: produce un checklist con hallazgos.

## Cuándo usarla

- Al terminar `proposal.md`/`design.md`/`spec.md` de un change que toque turnos, agenda, profesionales o boxes.
- Antes de marcar como hechas las tareas de Apply.
- Antes de archivar.

## Fuentes que hay que leer primero

1. `knowledge-base/04_reglas_de_negocio.md` (RN-01 a RN-06 y tabla de errores).
2. `knowledge-base/06_arquitectura.md` (capas y endpoints).
3. Las specs vigentes en `openspec/specs/`.

## Checklist de invariantes

Responder cada punto con ✅, ❌ (con archivo y línea) o N/A.

1. **Intervalo:** todo turno es `[inicio, fin)`. La superposición se calcula como `a.inicio < b.fin and a.fin > b.inicio`. Los turnos pegados se permiten.
2. **Zona horaria:** las entradas exigen offset explícito; se guarda y compara en UTC; el día del consultorio es UTC-03:00. Nada se redondea.
3. **No solapamiento:** se verifica por profesional **y** por box, dentro de la misma transacción que el INSERT o UPDATE. Prioridad de error: profesional antes que box.
4. **Concurrencia:** con SQLite, las escrituras usan `BEGIN IMMEDIATE`. Si el change agrega otra base, documenta un mecanismo equivalente y lo prueba con conexiones independientes; una prueba secuencial **no** demuestra concurrencia.
5. **Errores:** sólo los códigos `entrada_invalida` (422), `recurso_desconocido` (404), `conflicto_profesional`/`conflicto_box` (409) u otros nuevos declarados en la spec. Formato `{error, campo, mensaje}`. Un rechazo no modifica datos.
6. **Capas:** las reglas viven en `backend/odontologia/servicio.py`. `api.py` sólo adapta. El frontend no decide reglas de negocio.
7. **Datos:** sólo datos ficticios (`PAC-*`, `PRO-*`, `BOX-*`). Ningún nombre, DNI, teléfono o dato clínico real; ningún secreto en el repo.
8. **Pruebas:** cada escenario de la spec tiene al menos una prueba; hay evidencia RED antes de GREEN; la suite completa pasa.
9. **Alcance:** el change no agrega sobreturnos ni funcionalidades fuera de su `proposal.md`.

## Formato de salida

```markdown
## Revisión de dominio — <change>
| # | Invariante | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Intervalo [inicio, fin) | ✅ | servicio.py `_hay_solapamiento` |
...
**Bloqueantes:** <lista o "ninguno">
```

Si hay un ❌, el change no se archiva hasta corregirlo.
