import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const apiTarget = 'http://127.0.0.1:8000'
const wsTarget = 'ws://127.0.0.1:8000'

const proxy = {
  '/api': {
    target: apiTarget,
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api/, ''),
  },
  '/ws': {
    target: wsTarget,
    ws: true,
  },
}

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy,
  },
  preview: {
    port: 4173,
    proxy,
  },
})
