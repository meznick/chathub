import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  optimizeDeps: {
    exclude: ['fsevents'],
  },
  server: {
    // fill in dioc server address and port holding dev API service
    proxy: {
      '/login': {
        target: 'http://',
        secure: false,
        changeOrigin: false
      },
      '/register': {
        target: 'http://',
        secure: false,
        changeOrigin: false
      }
    }
  }
})
