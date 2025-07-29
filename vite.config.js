import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import { resolve } from "path";

export default defineConfig({
  base: "/static/",
  build: {
    manifest: "manifest.json",
    outDir: resolve("./assets"),
    assetsDir: "django-assets",
    // assetsDir: "static",
    rollupOptions: {
      input: {
        test: resolve("./static/js/main.js"),
      }
    }
  },
  plugins: [
    tailwindcss(),
  ],
})