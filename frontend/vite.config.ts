import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// En desarrollo, /api/* se reenvía al backend FastAPI local (puerto 8000),
// así el navegador no necesita CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (ruta) => ruta.replace(/^\/api/, ""),
      },
    },
  },
});
