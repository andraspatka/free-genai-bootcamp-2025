import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

import dotenv from 'dotenv';
dotenv.config();

const apiUrl = process.env.VITE_API_URL;

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  define: {
    __API_URL__: JSON.stringify(apiUrl),
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    },
    port: 8080,
  }
})