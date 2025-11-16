<template>
  <div class="min-h-screen bg-gradient-to-b from-green-50 to-white">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <NuxtLink to="/" class="flex items-center space-x-3">
            <img src="/logo.jpg" alt="Опора" class="w-12 h-12 rounded-lg object-cover">
            <h1 class="text-2xl font-bold text-gray-900">Опора</h1>
          </NuxtLink>
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
        </div>
      </div>
    </header>

    <!-- Login Form -->
    <main class="max-w-md mx-auto px-4 py-12">
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">Вход</h2>
        <p class="text-gray-600 mb-8">Войдите в свой аккаунт</p>

        <!-- Error Message -->
        <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-800 text-sm">{{ error }}</p>
        </div>

        <!-- Success Message -->
        <div v-if="success" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-green-800 text-sm">Вход выполнен! Перенаправление...</p>
        </div>

        <!-- Gosuslugi OAuth -->
        <button
          @click="loginWithGosuslugi"
          :disabled="loading"
          class="w-full mb-6 py-3 px-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center space-x-2 disabled:opacity-50"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 2a8 8 0 100 16 8 8 0 000-16zM9 9V5h2v4h4v2h-4v4H9v-4H5V9h4z"/>
          </svg>
          <span>Войти через Госуслуги</span>
        </button>

        <div class="relative mb-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-gray-300"></div>
          </div>
          <div class="relative flex justify-center text-sm">
            <span class="px-2 bg-white text-gray-500">или войдите по email</span>
          </div>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Ваш email"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
            <input
              v-model="form.password"
              type="password"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Ваш пароль"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-50"
          >
            {{ loading ? 'Вход...' : 'Войти' }}
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-gray-600">
          Нет аккаунта?
          <NuxtLink to="/register" class="text-primary-600 hover:text-primary-700 font-semibold">
            Зарегистрироваться
          </NuxtLink>
        </p>
      </div>

      <!-- Demo Credentials -->
      <div class="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p class="text-sm text-yellow-800 font-semibold mb-2">Демо доступ:</p>
        <p class="text-xs text-yellow-700">
          Создайте аккаунт через регистрацию или используйте Госуслуги (введите любой email)
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
const router = useRouter()
const config = useRuntimeConfig()
const { settings, updateSetting } = useAccessibility()

const form = ref({
  email: '',
  password: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

const toggleTheme = () => {
  const newTheme = settings.value.theme === 'light' ? 'dark' : 'light'
  updateSetting('theme', newTheme)
}

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  try {
    const response = await $fetch(`${config.public.apiBase}/auth/login/`, {
      method: 'POST',
      body: form.value
    })

    success.value = true

    // Save tokens
    localStorage.setItem('access_token', response.access)
    localStorage.setItem('refresh_token', response.refresh)

    // Fetch user info
    const user = await $fetch(`${config.public.apiBase}/auth/me/`, {
      headers: {
        Authorization: `Bearer ${response.access}`
      }
    })

    localStorage.setItem('user', JSON.stringify(user))

    // Redirect to dashboard
    setTimeout(() => {
      router.push('/dashboard')
    }, 1500)
  } catch (err) {
    console.error('Login error:', err)
    error.value = err.data?.non_field_errors?.[0] || err.data?.detail || 'Неверный email или пароль'
    loading.value = false
  }
}

const loginWithGosuslugi = async () => {
  loading.value = true
  error.value = ''

  // Mock Gosuslugi OAuth flow
  const mockEmail = prompt('Введите email для входа через Госуслуги (это демо):')

  if (!mockEmail) {
    loading.value = false
    return
  }

  try {
    const response = await $fetch(`${config.public.apiBase}/auth/oauth/gosuslugi/`, {
      method: 'POST',
      body: {
        email: mockEmail,
        beneficiary_category: 'pensioner',
        region: 'Москва'
      }
    })

    success.value = true

    // Save tokens
    localStorage.setItem('access_token', response.tokens.access)
    localStorage.setItem('refresh_token', response.tokens.refresh)
    localStorage.setItem('user', JSON.stringify(response.user))

    // Redirect to dashboard
    setTimeout(() => {
      router.push('/dashboard')
    }, 1500)
  } catch (err) {
    error.value = 'Ошибка входа через Госуслуги'
    loading.value = false
  }
}

useHead({
  title: 'Вход | Опора',
  meta: [
    { name: 'description', content: 'Войдите в систему для доступа к льготам' }
  ]
})
</script>
