import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

// In dev the backend runs elsewhere (docker: http://app:8000): Vite proxies /api so that
// frontend and API share the same origin, as in prod (D-010).
const apiProxyTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        // Never answer /api requests with the cached index.html (D-010).
        navigateFallbackDenylist: [/^\/api\//],
        // Precache the self-hosted font too (D-015), so it works offline.
        globPatterns: ['**/*.{js,css,html,svg,woff2}'],
      },
      manifest: {
        name: 'Fitter',
        short_name: 'Fitter',
        start_url: '/',
        display: 'standalone',
        background_color: '#FAFADF',
        theme_color: '#FAFADF',
        icons: [
          {
            src: 'icons/heart.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  server: {
    host: '0.0.0.0',
    port: 5173,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: apiProxyTarget,
      },
    },
  },
  build: {
    outDir: 'dist',
  }
})
