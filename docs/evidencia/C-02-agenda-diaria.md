# Evidencia — C-02 consultar-agenda-diaria

Pruebas ejecutadas por el agente de IA (Claude) el 2026-11-16 (Linux, Python 3.13.18, Node 22.23.4). **No son una verificación del alumno.**

## RED (backend)

Se escribió `tests/test_agenda_diaria.py` antes de `consultar_agenda`:

```text
$ python -m unittest discover -s tests -t .
ImportError: cannot import name 'consultar_agenda' from 'odontologia.servicio'
Ran 25 tests in 0.383s
FAILED (errors=1)
```

## GREEN (backend, suite completa C-01 + C-02)

```text
$ python -W error::DeprecationWarning -m unittest discover -s tests -t .
Ran 38 tests in 0.854s
OK
```

## Frontend: lógica de la pantalla

```text
$ npm test        # tsx --test src/agenda.test.ts
# tests 10
# pass 10
# fail 0
```

`src/agenda.ts` y `src/agenda.test.ts` pasaron `tsc --strict` en el entorno del agente. En ese entorno no se pudo correr `npm install`; `npm run build` se verificó luego en la PC del alumno (ver al final).

## Prueba manual de la API

```text
$ curl "localhost:8123/agenda?fecha=2026-12-01"
{"fecha":"2026-12-01","zona_horaria":"-03:00","turnos":[{"id":1,...,"inicio":"2026-12-01T12:00:00Z",
 "fin":"2026-12-01T12:30:00Z","paciente_nombre":"Paciente Ficticio Uno","profesional_nombre":"Odontóloga Ficticia A","box_nombre":"Box 1"}]}   → 200
```

## Cobertura de escenarios de la spec

| Requirement | Pruebas |
| --- | --- |
| Consulta por día local | `ServicioAgenda.test_devuelve_solo_el_dia_pedido_ordenado`, `test_turno_que_cruza_medianoche_aparece_en_ambos_dias`, `test_dia_sin_turnos_devuelve_lista_vacia`, `ApiAgenda.test_get_agenda_200`, `test_get_agenda_vacia_200` |
| Orden estable | `test_empate_de_hora_se_ordena_por_id` |
| Filtros validados | `test_filtra_por_profesional_y_por_box`, `test_filtro_desconocido_o_mal_formado`, `ApiAgenda.test_get_agenda_profesional_desconocido_404` |
| Fecha obligatoria y válida | `test_fecha_invalida`, `ApiAgenda.test_get_agenda_sin_fecha_422`, `test_get_agenda_fecha_mal_escrita_422` |
| Datos para mostrar | `test_incluye_nombres_ficticios_para_mostrar`, `ApiAgenda.test_catalogo_para_filtros` |
| Pantalla "Agenda del día" | `agenda.test.ts` (conversión de hora, cruce de medianoche, hoy local, mensajes de error); estados de la pantalla: verificación manual |

## Revisión con la skill `odontologia-turnos`

Realizada por el agente antes de archivar.

| # | Invariante | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Intervalo `[inicio, fin)` | ✅ | `consultar_agenda` usa `Turno.inicio < hasta` y `Turno.fin > desde`, la misma fórmula de C-01 |
| 2 | Zona horaria / UTC | ✅ | `ZONA_CONSULTORIO = -03:00`; la API responde en UTC; el frontend convierte sólo para mostrar |
| 3 | No solapamiento | N/A | C-02 sólo lee |
| 4 | Concurrencia | N/A | Sin escrituras |
| 5 | Errores | ✅ | Reutiliza `entrada_invalida` y `recurso_desconocido` con `{error, campo, mensaje}` |
| 6 | Capas | ✅ | Reglas en `servicio.py`; `agenda.ts` sólo da formato |
| 7 | Datos ficticios | ✅ | Sólo `PAC-*`, `PRO-*`, `BOX-*` y nombres "Ficticio" |
| 8 | Pruebas | ✅ | Hay prueba para cada escenario; RED registrado; suites verdes |
| 9 | Alcance | ✅ | Sin alta desde la pantalla (queda para C-06) |

**Bloqueantes:** ninguno.

## Verificación en la PC del alumno

2026-11-16, Windows, `powershell -ExecutionPolicy Bypass -File scripts\verificar.ps1`: backend `Ran 38 tests ... OK`, frontend con pruebas y build correctos, `openspec validate --all --strict` 2 passed / 0 failed. Resultado: `TODO OK`.
