import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 10880,
    strictPort: true,
    host: true,
    proxy: {
      "/api": { target: "http://127.0.0.1:10881", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:10881", changeOrigin: true },
    },
  },
});
