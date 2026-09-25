import { defineConfig } from "vite";

export default defineConfig({
  clearScreen: false,
  server: { strictPort: true, port: 1420 },
  envPrefix: ["VITE_"],
  build: { target: ["es2021", "chrome100", "safari13"] },
});
