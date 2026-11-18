# MCP: Context7

[Context7](https://github.com/upstash/context7) es un servidor MCP que le da al agente documentación **actualizada y por versión** de librerías (Vite, SQLAlchemy, FastAPI, React…), en lugar de depender de lo que el modelo recuerda de su entrenamiento.

## 1. Conexión

Se usó el conector **Context7** de claude.ai (sin claves en el repositorio):

1. En claude.ai, buscar el conector **Context7** y tocar *Conectar*; autorizar con la cuenta.
2. Comprobación (2026-11-18): el agente listó los conectores y Context7 apareció como `installState: connected`, `enabledInChat: true`, con sus dos herramientas disponibles.

Alternativa para Claude Code (mismo servidor, local):

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp
claude mcp list          # debe mostrar: context7 ✓ connected
```

Sólo se consulta documentación pública. Nunca se envían datos del consultorio, claves ni código propietario en las consultas.

## 2. Capacidades

| Herramienta | Qué hace |
| --- | --- |
| `resolve-library-id` | Busca una librería por nombre y devuelve su ID de Context7, versiones disponibles y calidad de la fuente. |
| `query-docs` | Trae documentación y ejemplos de un tema concreto de esa librería (opcionalmente de una versión exacta). |

## 3. Uso real y aplicación a los changes

Las consultas se hicieron el 2026-11-18, **después** de implementar C-02 y C-04, como **verificación** de dos decisiones de diseño contra la documentación oficial de la versión usada. La consigna admite usar el MCP en la preparación, implementación **o verificación** de un change.

### Consulta 1 — C-02: proxy de Vite (`frontend/vite.config.ts`)

| Paso | Detalle |
| --- | --- |
| Solicitud | `resolve-library-id` con *Vite* → elegido `/vitejs/vite` (reputación High, incluye la versión **v6.4.5**, la misma rama que usa el proyecto: Vite 6.4.6). |
| | `query-docs` en `/vitejs/vite/v6.4.5`: *"server.proxy option: forward /api requests to http://127.0.0.1:8000 with changeOrigin and rewrite that removes the /api prefix"* |
| Resultado | La documentación oficial (`docs/config/server-options.md` de v6.4.5) muestra exactamente el patrón `'/api': { target, changeOrigin: true, rewrite: (path) => path.replace(/^\/api/, '') }` y aclara que las peticiones que coinciden con una regla de proxy no son transformadas por Vite. |
| Revisión | Se comparó línea por línea con `frontend/vite.config.ts`: mismo `target`, `changeOrigin: true` y el mismo `rewrite`. **Coincide.** Además, la doc aclara que con un `base` no relativo hay que prefijar las claves; el proyecto usa la base por defecto, así que no aplica. |
| Aporte | Confirma con la doc de la versión exacta la decisión D5 del design de C-02 (pantalla y API en el mismo origen, sin CORS). El mismo mapeo se replicó en `frontend/nginx.conf` para Docker (C-04). |

### Consulta 2 — C-04: bloqueo de filas con SQLAlchemy (`backend/odontologia/servicio.py`)

| Paso | Detalle |
| --- | --- |
| Solicitud | `resolve-library-id` con *SQLAlchemy* → elegido `/websites/sqlalchemy_en_20_orm` (documentación oficial del ORM 2.0, reputación High). |
| | `query-docs`: *"Select.with_for_update() to emit SELECT ... FOR UPDATE row locks inside a Session transaction, and behavior on SQLite"* |
| Resultado | La doc confirma que `with_for_update()` sin argumentos agrega `FOR UPDATE` al `SELECT`. Advierte que **no se recomienda combinarlo con eager loading / `joinedload()`**, porque puede bloquear también las tablas unidas. |
| Revisión | En `registrar_turno` el bloqueo se hace con `select(modelo.id).where(modelo.id == …).with_for_update()`: un `SELECT` simple, sin joins ni carga ansiosa, así que la advertencia no aplica. La doc no respondió el comportamiento en SQLite, así que se comprobó compilando la consulta: |

```text
sqlite    : SELECT profesionales.id FROM profesionales WHERE profesionales.id = ?
postgresql: SELECT profesionales.id FROM profesionales WHERE profesionales.id = %(id_1)s FOR UPDATE
```

| | |
| --- | --- |
| Aporte | Confirma la decisión D1/D3 del design de C-04: el mismo código bloquea filas en PostgreSQL y en SQLite no emite `FOR UPDATE` (ahí protege `BEGIN IMMEDIATE`). También deja documentado un riesgo a evitar en changes futuros: no usar `joinedload()` en consultas con `FOR UPDATE`. |

## 4. Cómo se revisó el resultado

- No se aceptó la respuesta del MCP "porque sí": se la contrastó con el código del repositorio y, cuando la documentación no respondía algo (SQLite), se comprobó ejecutando código.
- Las pruebas que respaldan ambas decisiones siguen en verde: 17 pruebas de frontend y 65 de backend, incluida la concurrencia en PostgreSQL (ver `docs/evidencia/`).
