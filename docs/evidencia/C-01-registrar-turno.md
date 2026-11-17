# Evidencia — C-01 registrar-turno-sin-solapamientos

Pruebas ejecutadas por el agente de IA (Claude) el 2026-11-16 en un entorno Linux con Python 3.13.18. Las versiones de las librerías en ese entorno fueron FastAPI 0.115.12, SQLAlchemy 2.0.40 y Pydantic 1.10.21; el código no depende de APIs propias de una versión de Pydantic. **Estas ejecuciones no son una verificación del alumno.** Para repetirlas, ver el README.

## RED

Se escribieron `tests/test_registro_turnos.py` y `tests/test_api_turnos.py` antes del código:

```text
$ python -m unittest discover -s tests -t .
ModuleNotFoundError: No module named 'odontologia.db'
Ran 2 tests in 0.000s
FAILED (errors=2)
```

## GREEN

Después de implementar `db.py`, `servicio.py` y `api.py`:

```text
$ python -m unittest discover -s tests -t .
Ran 24 tests in 0.403s
OK
```

## Concurrencia: prueba de mutación

La prueba `Concurrencia.test_dos_altas_simultaneas_del_mismo_profesional` se corrió 5 veces con cada variante:

| Variante en `db.py` | Resultado |
| --- | --- |
| `BEGIN` común (mutación) | 4 de 5 FALLARON (se colaron dos turnos o hubo error de lock) |
| `BEGIN IMMEDIATE` (implementación) | 5 de 5 OK |

Conclusión: la prueba detecta la condición de carrera y `BEGIN IMMEDIATE` la evita.

## Prueba manual con Uvicorn

```text
$ uvicorn odontologia.api:crear_app --factory --port 8123
$ curl localhost:8123/health
{"estado":"ok"}
$ curl -X POST localhost:8123/turnos -H 'content-type: application/json' \
  -d '{"paciente_id":"PAC-001","profesional_id":"PRO-001","box_id":"BOX-1","inicio":"2026-12-01T09:00:00-03:00","fin":"2026-12-01T09:30:00-03:00"}'
{"id":1,"paciente_id":"PAC-001","profesional_id":"PRO-001","box_id":"BOX-1","inicio":"2026-12-01T12:00:00Z","fin":"2026-12-01T12:30:00Z"}   → 201
$ curl -o /dev/null -w "%{http_code}" localhost:8123/docs
200
```

## Cobertura de escenarios de la spec

| Requirement | Pruebas |
| --- | --- |
| Catálogo ficticio preparado | `setUp` de cada prueba; `AltaValida.test_persiste_al_reabrir_la_agenda` |
| Validación de identificadores | `EntradasInvalidas.test_campos_obligatorios`, `test_identificadores_mal_formados`, `test_cuerpo_que_no_es_objeto` |
| Recursos existentes | `EntradasInvalidas.test_recursos_desconocidos_en_orden`, `ApiTurnos.test_recurso_desconocido_devuelve_404` |
| Fechas con zona y minutos | `test_fecha_sin_offset_o_mal_escrita`, `test_precision_de_minutos`, `test_intervalo_vacio_o_invertido`, `AltaValida.test_registra_y_devuelve_instantes_en_utc` |
| Sin solapamiento | Clase `Solapamientos` (5 patrones × profesional y box, prioridad, adyacencia, simultáneos, rechazo sin cambios), `test_offsets_equivalentes_representan_el_mismo_instante` |
| Altas simultáneas | `Concurrencia.test_dos_altas_simultaneas_del_mismo_profesional` |
| Contrato HTTP | Clase `ApiTurnos` (201, 404, 409, 422, JSON mal formado, health) |

Lint: `ruff check odontologia tests` → `All checks passed!`
