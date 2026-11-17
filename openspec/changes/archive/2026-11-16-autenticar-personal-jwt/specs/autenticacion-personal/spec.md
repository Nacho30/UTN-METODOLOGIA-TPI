## ADDED Requirements

### Requirement: Usuarios ficticios con clave protegida
El sistema SHALL preparar tres usuarios ficticios: `recepcion` (rol `recepcion`), `profesional` (rol `profesional`) y `admin` (rol `administracion`), con la clave indicada en `ODONTOLOGIA_CLAVE_DEMO` (mínimo 8 caracteres). Si la variable no está definida SHALL no crear usuarios y emitir una advertencia. Las claves SHALL guardarse sólo como hash PBKDF2-SHA256 con sal aleatoria y MUST NOT figurar en el repositorio ni guardarse en texto plano.

#### Scenario: Sin clave de demostración
- **WHEN** se inicia sin `ODONTOLOGIA_CLAVE_DEMO`
- **THEN** se emite una advertencia y cualquier login responde 401 `credenciales_invalidas`

#### Scenario: Clave de demostración corta
- **WHEN** `ODONTOLOGIA_CLAVE_DEMO` tiene menos de 8 caracteres
- **THEN** el inicio falla con un error de configuración

#### Scenario: Sólo el hash en la base
- **WHEN** se crean los usuarios
- **THEN** la base guarda un hash que no contiene la clave

#### Scenario: Hash de clave
- **WHEN** se hashea una clave
- **THEN** el resultado empieza con `pbkdf2_sha256$`, no contiene la clave y la misma clave hasheada dos veces da resultados distintos

#### Scenario: Hash mal formado
- **WHEN** se verifica una clave contra un hash vacío o de otro esquema
- **THEN** la verificación da falso sin error

### Requirement: Inicio de sesión con JWT
`POST /auth/login` con `{usuario, clave}` SHALL devolver 200 con `access_token` (JWT HS256), `token_type` `bearer`, `expira_en` en segundos (1800 por defecto), `usuario` y `rol`. El token SHALL incluir `sub`, `rol`, `jti`, `iat` y `exp`. Usuario inexistente y clave incorrecta SHALL responder igual: 401 `credenciales_invalidas`. Datos mal formados SHALL responder 422 `entrada_invalida`.

#### Scenario: Login correcto
- **WHEN** `recepcion` inicia sesión con la clave de demostración
- **THEN** recibe un JWT válido con `rol` `recepcion`

#### Scenario: Credenciales incorrectas
- **WHEN** se usa una clave incorrecta o un usuario inexistente
- **THEN** ambas respuestas son idénticas: 401 `credenciales_invalidas`

#### Scenario: Cuerpo inválido
- **WHEN** falta `clave`, `usuario` está vacío o el cuerpo no es un objeto
- **THEN** se responde 422 `entrada_invalida`

### Requirement: Rutas protegidas
Todas las rutas salvo `GET /health` y `POST /auth/login` SHALL exigir `Authorization: Bearer <token>`. Sin cabecera Bearer SHALL responder 401 `no_autenticado`; con un token mal formado, firmado con otro secreto, vencido, sin `jti`, con rol desconocido, con algoritmo `none` o revocado SHALL responder 401 `token_invalido`. Toda respuesta 401 SHALL incluir `WWW-Authenticate: Bearer`.

#### Scenario: Sin token
- **WHEN** se consulta `GET /agenda` sin cabecera
- **THEN** se responde 401 `no_autenticado` con `WWW-Authenticate: Bearer`

#### Scenario: Token vencido o manipulado
- **WHEN** el token venció o fue firmado con otro secreto
- **THEN** se responde 401 `token_invalido`

#### Scenario: Salud pública
- **WHEN** se consulta `GET /health` sin token
- **THEN** se responde 200

### Requirement: Permisos por rol
El backend SHALL aplicar esta matriz antes de leer el cuerpo de la solicitud: registrar turnos → `recepcion`, `administracion`; consultar agenda y catálogo → `recepcion`, `profesional`, `administracion`. Un rol sin permiso SHALL recibir 403 `sin_permiso`.

#### Scenario: Profesional intenta registrar
- **WHEN** el usuario `profesional` hace `POST /turnos`
- **THEN** se responde 403 `sin_permiso`, aunque el cuerpo sea inválido

#### Scenario: Profesional consulta la agenda
- **WHEN** el usuario `profesional` consulta `GET /agenda`
- **THEN** se responde 200

### Requirement: Cierre de sesión con Redis
`POST /auth/logout` SHALL revocar el `jti` del token hasta su vencimiento y responder 204. Con `ODONTOLOGIA_REDIS_URL` la revocación SHALL guardarse en Redis con clave `odontologia:revocado:<jti>` y TTL igual al tiempo restante del token; sin Redis SHALL guardarse en memoria del proceso. Cerrar una sesión MUST NOT afectar otras sesiones del mismo usuario.

#### Scenario: Token cerrado
- **WHEN** se cierra la sesión y se vuelve a usar el mismo token
- **THEN** se responde 401 `token_invalido`

#### Scenario: Revocación en Redis
- **GIVEN** Redis configurado
- **WHEN** se cierra la sesión
- **THEN** existe la clave `odontologia:revocado:<jti>` con TTL de como máximo 30 minutos

#### Scenario: Otra sesión sigue activa
- **WHEN** el mismo usuario tiene dos sesiones y cierra una
- **THEN** la otra sigue funcionando

### Requirement: Secreto de firma configurable
El secreto JWT SHALL leerse de `ODONTOLOGIA_JWT_SECRETO` y MUST tener al menos 32 caracteres; si es más corto el sistema SHALL negarse a iniciar. Si no está definido, SHALL generarse uno temporal al iniciar y emitir una advertencia. El secreto MUST NOT guardarse en el repositorio.

#### Scenario: Secreto corto
- **WHEN** se inicia con un secreto de 5 caracteres
- **THEN** el inicio falla con un error de configuración

### Requirement: Pantalla de ingreso
El frontend SHALL pedir usuario y clave antes de mostrar la agenda, enviar el token en cada pedido, mostrar el usuario y su rol con un botón "Salir" y volver al ingreso cuando la API responda 401. La sesión SHALL guardarse en `sessionStorage` y la app MUST seguir funcionando si el navegador bloquea el almacenamiento.

#### Scenario: Sesión vencida
- **WHEN** la API responde 401 mientras se ve la agenda
- **THEN** la pantalla vuelve al ingreso con el aviso de sesión vencida

#### Scenario: Formulario incompleto
- **WHEN** se intenta ingresar sin clave
- **THEN** se muestra "Ingresá la clave." sin llamar a la API
