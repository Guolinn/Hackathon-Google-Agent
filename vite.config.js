import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://crisisflow-backend-556676992179.us-central1.run.app',
        changeOrigin: true,
        secure: true,
      },
    },
  },
})
