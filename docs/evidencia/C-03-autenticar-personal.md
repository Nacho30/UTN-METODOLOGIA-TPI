# Evidencia — C-03 autenticar-personal-jwt

Pruebas ejecutadas por el agente de IA (Claude) el 2026-11-16 (Linux, Python 3.13, PyJWT 2.10.1, redis-py 5.2.1, Redis 7.0.15, Node 22). **No son una verificación del alumno.**

## RED

Backend, con `tests/test_autenticacion.py` escrito y las pruebas de C-01/C-02 adaptadas para iniciar sesión:

```text
$ python -m unittest discover -s tests -t .
ModuleNotFoundError: No module named 'odontologia.autenticacion'
ImportError: cannot import name 'CLAVE_DEMO' from 'odontologia.datos_demo'
FAILED (errors=4)
```

Frontend, con `src/sesion.test.ts` escrito:

```text
$ npm test
Error [ERR_MODULE_NOT_FOUND]: Cannot find module '.../src/sesion.ts'
```

## GREEN

```text
# Sin Redis (las 3 pruebas de Redis se omiten)
$ python -W error::DeprecationWarning -m unittest discover -s tests -t .
Ran 62 tests ... OK (skipped=3)

# Con Redis real
$ ODONTOLOGIA_TEST_REDIS_URL=redis://127.0.0.1:56379/0 python -m unittest discover -s tests -t .
Ran 62 tests ... OK

$ npm test
# tests 17   # pass 17   # fail 0

$ ruff check odontologia tests
All checks passed!
```

## Prueba manual (Uvicorn + PostgreSQL + Redis)

```text
POST /auth/login  {"usuario":"recepcion","clave":"<clave de demo>"}     → 200 con access_token
POST /turnos  (con Bearer)                                              → 201
POST /turnos  (sin token)                                               → 401 {"error":"no_autenticado",...}
GET  /agenda?fecha=2026-12-01 (con Bearer)                              → 200
POST /auth/logout                                                       → 204
redis-cli keys '*'                                                      → odontologia:revocado:92b0e84c…
GET  /catalogo  (mismo token)                                           → 401 {"error":"token_invalido",...}
```

Swagger (`/openapi.json`) expone el esquema `HTTPBearer`, así aparece el botón **Authorize**.

## Cobertura de la spec `autenticacion-personal`

| Requirement | Pruebas |
| --- | --- |
| Usuarios con clave protegida | `Claves.*`, `Configuracion.test_sin_clave_demo_no_hay_usuarios`, `test_clave_demo_corta_se_rechaza`, `test_clave_demo_se_guarda_solo_como_hash` |
| Inicio de sesión con JWT | `Login.*` |
| Rutas protegidas | `ProteccionDeRutas.test_sin_token`, `test_tokens_invalidos` (6 casos), `test_esquema_que_no_es_bearer`, `test_health_es_publico` |
| Permisos por rol | `Matriz.test_matriz_de_permisos`, `test_profesional_no_puede_registrar_turnos`, `test_recepcion_y_administracion_registran`, `test_permiso_se_evalua_antes_que_los_datos` |
| Cierre de sesión con Redis | `CerrarSesion.*`, `RevocacionesEnRedis.*`, `Configuracion.test_revocaciones_en_memoria_vencen` |
| Secreto configurable | `Configuracion.test_secreto_corto_se_rechaza_al_iniciar` |
| Pantalla de ingreso | `sesion.test.ts` (7 pruebas); el flujo en el navegador se verifica a mano |

## Corrección de auditoría (clave fuera del repo)

Se movió la clave de demostración a `ODONTOLOGIA_CLAVE_DEMO` (ver design D3b). Resultado después de la corrección:

```text
$ python -W error::DeprecationWarning -m unittest discover -s tests -t .
Ran 65 tests ... OK (skipped=3)

$ ODONTOLOGIA_TEST_REDIS_URL=… ODONTOLOGIA_TEST_DB_URL=postgresql+psycopg://… python -m unittest discover -s tests -t .
Ran 65 tests ... OK      (tres corridas seguidas)
```

## Revisión con la skill `odontologia-turnos`

| # | Invariante | Resultado | Evidencia |
| --- | --- | --- | --- |
| 1 | Intervalo `[inicio, fin)` | ✅ | Sin cambios en `_hay_solapamiento` |
| 2 | Zona horaria / UTC | ✅ | Sin cambios |
| 3 | No solapamiento | ✅ | Las pruebas de C-01 siguen pasando con sesión |
| 4 | Concurrencia | ✅ | Sin cambios en la transacción |
| 5 | Errores | ✅ | 4 códigos nuevos declarados en la spec, mismo formato |
| 6 | Capas | ✅ | Permisos en `autenticacion.PERMISOS` (backend); el frontend sólo reenvía el token |
| 7 | Datos ficticios / secretos | ✅ | Usuarios ficticios, sólo hash en la base; secreto JWT por variable de entorno |
| 8 | Pruebas | ✅ | RED registrado, todos los escenarios cubiertos |
| 9 | Alcance | ✅ | Sin gestión de usuarios ni refresh tokens |
| 10 | Seguridad | ✅ | Todas las rutas salvo `/health` y login protegidas; `alg: none` rechazado; mismo error ante usuario o clave incorrectos |

**Bloqueantes:** ninguno.
