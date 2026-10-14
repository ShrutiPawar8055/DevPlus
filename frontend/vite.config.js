import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Vite configuration. The proxy forwards /api requests to the FastAPI backend
// so the frontend and backend share the same origin during development.
export default defineConfig({
    plugins: [react()],
    server: {
        port: 5173,
        proxy: {
            "/api": {
                target: "http://localhost:8000",
                changeOrigin: true,
            },
        },
    },
});
