import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  optimizeDeps: {
    exclude: ['fsevents'],
  },
  server: {
    proxy: {
      '/login': {
        target: 'http://161.35.194.242:8888',
        secure: false,
        changeOrigin: false
      },
      '/register': {
        target: 'http://161.35.194.242:8888',
        secure: false,
        changeOrigin: false
      }
    }
  }
})
