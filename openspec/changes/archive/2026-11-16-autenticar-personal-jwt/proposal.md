# Proposal — C-03 autenticar-personal-jwt

## Why

Hasta C-02 cualquiera que llegue a la API puede registrar o ver turnos. El Discovery (D-03) pide que sólo el personal autorizado modifique la agenda, y la cátedra fijó **JWT** y **Redis** como parte del stack obligatorio. En el Parcial 2 la corrección fue justamente no respetar el stack completo; este change lo cumple.

## What Changes

- Usuarios ficticios `recepcion`, `profesional` y `admin` con clave guardada como hash PBKDF2.
- `POST /auth/login` emite un JWT HS256 (30 minutos) con `sub`, `rol`, `jti`, `iat`, `exp`.
- `POST /auth/logout` revoca el token guardando su `jti` en **Redis** con TTL; sin Redis, en memoria.
- `GET /auth/yo` devuelve el usuario de la sesión.
- Todas las rutas (salvo `/health` y el login) exigen `Authorization: Bearer`. Matriz de permisos por rol en el backend.
- Errores nuevos: `credenciales_invalidas`, `no_autenticado`, `token_invalido` (401) y `sin_permiso` (403).
- Frontend: pantalla de ingreso, token en cada pedido, botón "Salir" y vuelta al ingreso ante 401.
- Swagger con botón **Authorize** (esquema Bearer).

## Capabilities

### New Capabilities

- `autenticacion-personal`: login JWT, permisos por rol y cierre de sesión con Redis.

### Modified Capabilities

- `registro-turnos`: `POST /turnos` exige sesión con rol `recepcion` o `administracion`.
- `agenda-diaria`: `GET /agenda` y `GET /catalogo` exigen sesión.

## Fuera de alcance

Alta y edición de usuarios, recuperación de clave, refresh tokens, límite de intentos de login, HTTPS (la API es local) y que cada profesional vea sólo su agenda.

## Impact

- Backend: `autenticacion.py` nuevo, modelo `Usuario`, dependencias de sesión y permiso en `api.py`.
- Dependencias: `pyjwt`, `redis`.
- Frontend: `sesion.ts` nuevo y `App.tsx` con login.
- Las pruebas de C-01 y C-02 pasan a iniciar sesión antes de llamar a la API.
