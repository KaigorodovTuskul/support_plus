// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false, // Disable SSR to avoid Windows path issues in development

  // Pages directory configuration
  dir: {
    pages: 'pages'
  },

  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt',
    // '@vite-pwa/nuxt', // Temporarily disabled due to Windows path issue
  ],

  app: {
    head: {
      title: 'ПОДДЕРЖКА+ | Льготы и скидки',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Доступ к государственным льготам и коммерческим скидкам для льготников' },
        { name: 'theme-color', content: '#16a34a' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
      ],
    },
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL || 'http://localhost:8000/api',
    },
  },

  // PWA configuration - will be re-enabled after Windows path issues are resolved
  // pwa: {
  //   manifest: {
  //     name: 'SUPPORT+',
  //     short_name: 'SUPPORT+',
  //     description: 'Доступ к льготам и скидкам для льготников',
  //     theme_color: '#4f46e5',
  //     background_color: '#ffffff',
  //   },
  // },

  typescript: {
    shim: false,
  },

  tailwindcss: {
    cssPath: '~/assets/css/main.css',
    configPath: 'tailwind.config.js',
  },

  components: true,  // Re-enable components auto-import

  imports: {
    autoImport: true,  // Re-enable auto-imports
  },
  ignore: [
    '**/vite/modulepreload-polyfill.js',
    '**/*.test.*',
    '**/*.spec.*'
  ],
  vite: {
    server: {
      watch: {
        ignored: ['**/vite/**']
      }
    }
  }
})
