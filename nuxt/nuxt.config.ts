import Components from 'unplugin-vue-components/vite';
import { PrimeVueResolver } from 'unplugin-vue-components/resolvers'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: [
    '@nuxt/eslint', 
    '@nuxt/ui', 
    '@nuxthq/ui', 
    'nuxt-lucide-icons', 
    '@pinia/nuxt'
          ],

  vite: {
    plugins: [
      Components({
        resolvers: [PrimeVueResolver()]
      })
    ],
    optimizeDeps: {
      include: [
        '@vee-validate/zod',
        'vee-validate',
        'zod',
      ]
    }
  },

  ssr: false,

  devtools: {
    enabled: true,

    timeline: {
      enabled: true
    }
  },

  css: ['~/assets/css/main.css'],

  ui: {
    theme: {
      colors: [
        'primary',
        'primary-foreground',
        'info',
        'secondary',
        'success',
        'error',
        'neutral',
        'warning'
      ]
    }
  },

  runtimeConfig: {
    secretKey: process.env.SECRET_KEY || 'secret_key',
    public: {
      apiBaseAuth: process.env.API_BASE_AUTH || 'localhost:8001',
      apiBaseDatasets: process.env.API_BASE_DATASETS || 'localhost:8002',
      apiBaseModels: process.env.API_BASE_MODELS || 'localhost:8003',
      apiBaseProjects: process.env.API_BASE_PROJECS || 'localhost:8004'
    }
  },

  routeRules: {
    '/': { prerender: true }
  },

  compatibilityDate: '2025-01-15',

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
