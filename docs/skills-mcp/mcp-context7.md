# MCP: Context7

[Context7](https://github.com/upstash/context7) es un servidor MCP que le da al agente documentación **actualizada** de librerías (FastAPI, SQLAlchemy, Vite, React) en lugar de depender de lo que recuerda el modelo.

## 1. Conexión (Claude Code)

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp
claude mcp list          # debe mostrar: context7 ✓ connected
```

Sólo se consulta documentación pública. Nunca se envían datos del proyecto ni del consultorio.

## 2. Uso real de la herramienta
El MCP expone dos herramientas: `resolve-library-id` (busca la librería) y `get-library-docs` (trae la documentación de un tema).

Consulta aplicada a C-02:

1. `resolve-library-id` con `vite` → `/vitejs/vite`.
2. `get-library-docs` con `/vitejs/vite`, tema `server.proxy rewrite`.

## 3. Aplicación a un change
La respuesta sirve para justificar la configuración de [`frontend/vite.config.ts`](../../frontend/vite.config.ts) de C-02: `server.proxy['/api']` con `target: 'http://127.0.0.1:8000'`, `changeOrigin` y `rewrite` que quita `/api`. Así el navegador habla con el mismo origen y el backend no necesita CORS (design de C-02, D5).

## Evidencia

> ⚠️ **Pendiente de ejecutar por el alumno.** El entorno donde el agente armó el repo no tenía Context7 conectado, así que esta consulta **no** se hizo todavía. Para completarla: conectar el MCP con el comando de arriba, pedirle al agente *"usá Context7 para buscar en la documentación de Vite cómo configurar server.proxy con rewrite"*, sacar captura y pegar abajo el resultado y la fecha.

| Fecha | Herramienta | Consulta | Resultado |
| --- | --- | --- | --- |
| _pendiente_ | | | |
