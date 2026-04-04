// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/eslint', '@nuxt/ui', 'nuxt-lucide-icons'],
  
  runtimeConfig: {
    secretKey: process.env.SECRET_KEY || "secret_key"
  },

  ssr: true,

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
        'warning',
      ],
    },
  },

  devtools: {
    enabled: true,

    timeline: {
      enabled: true
    }
  },

  css: ['~/assets/css/main.css'],

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