import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@lang-config': path.resolve(__dirname, '../backend/config'),
    },
  },
  server: {
    port: 3000,
    strictPort: true, // 3000 被佔用時直接失敗，不自動改用 3001
    host: '0.0.0.0', // 監聽所有網絡接口，包括 IPv4 和 IPv6
    open: true,
  },
})

