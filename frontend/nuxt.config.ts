// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: process.env.NUXT_DEVTOOLS !== 'false' },
  app: {
    head: {
      title: 'Бронирование | Simadancing',
      meta: [
        {
          name: 'viewport',
          content: 'width=device-width, initial-scale=1, viewport-fit=cover',
        },
      ],
    }
  },

  modules: [
    '@nuxt/eslint',
    '@nuxt/image',
    '@nuxt/scripts',
    '@nuxt/test-utils',
    '@nuxt/ui',
    '@pinia/nuxt',
    'pinia-plugin-persistedstate'
  ],
  runtimeConfig: {
    backendUrl: process.env.NUXT_BACKEND_URL || process.env.BACKEND_URL || 'http://localhost:8000',
    public: {
      backendWsUrl: process.env.NUXT_PUBLIC_BACKEND_WS_URL || ''
    }
  },
  css: ['~/assets/css/main.css']
})
