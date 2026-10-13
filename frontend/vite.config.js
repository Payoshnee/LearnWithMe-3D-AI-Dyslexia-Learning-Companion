import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
export default defineConfig({ assetsInclude: ['**/*.glb'], plugins: [react()], server: { port: 5173 }, build: { sourcemap: true } })
