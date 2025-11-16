<template>
  <header class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <div class="flex items-center justify-between">
        <NuxtLink :to="backLink" class="flex items-center space-x-3">
          <img src="/logo.jpg" alt="Опора" class="w-12 h-12 rounded-lg object-cover">
          <h1 class="text-2xl font-bold text-gray-900">Опора</h1>
        </NuxtLink>

        <div class="flex items-center space-x-3">
          <!-- Accessibility Settings Link -->
          <NuxtLink
            to="/settings"
            class="p-2 text-gray-600 hover:text-gray-900 transition focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
            title="Настройки доступности"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </NuxtLink>

          <!-- Theme Switcher -->
          <button
            @click="toggleTheme"
            class="p-2 text-gray-600 hover:text-gray-900 transition focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
            :title="settings.theme === 'light' ? 'Включить темную тему' : 'Включить светлую тему'"
          >
            <svg v-if="settings.theme === 'light'" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </button>

          <span v-if="showUser" class="text-gray-700 hidden sm:inline">{{ username }}</span>

          <button
            v-if="showLogout"
            @click="handleLogout"
            class="text-red-600 hover:text-red-700 font-semibold focus:outline-none focus:ring-2 focus:ring-red-500 rounded px-2 py-1"
          >
            Выход
          </button>

          <NuxtLink
            v-if="showBackButton"
            :to="backLink"
            class="text-gray-600 hover:text-gray-900 font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-2 py-1"
          >
            Назад
          </NuxtLink>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
const router = useRouter()
const { settings, updateSetting } = useAccessibility()

const props = defineProps({
  showUser: {
    type: Boolean,
    default: true
  },
  showLogout: {
    type: Boolean,
    default: true
  },
  showBackButton: {
    type: Boolean,
    default: false
  },
  backLink: {
    type: String,
    default: '/dashboard'
  },
  username: {
    type: String,
    default: 'Пользователь'
  }
})

const toggleTheme = () => {
  const newTheme = settings.value.theme === 'light' ? 'dark' : 'light'
  updateSetting('theme', newTheme)
}

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('user')
  router.push('/')
}
</script>
