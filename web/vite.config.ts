import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  build: { outDir: "../backend/src/sensor_workbench/static", emptyOutDir: true },
  server: {
    proxy: {
      "/api": { target: "http://127.0.0.1:8765", ws: true, changeOrigin: false },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    restoreMocks: true,
  },
});
