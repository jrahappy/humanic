import { defineConfig } from "vite";
import { resolve } from "path";
import tailwindcss from '@tailwindcss/vite'

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