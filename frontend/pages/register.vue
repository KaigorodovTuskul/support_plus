<template>
  <div class="min-h-screen bg-gradient-to-b from-green-50 to-white">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <NuxtLink to="/" class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-white text-xl font-bold">П+</span>
            </div>
            <h1 class="text-2xl font-bold text-gray-900">ПОДДЕРЖКА+</h1>
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

    <!-- Registration Form -->
    <main class="max-w-md mx-auto px-4 py-12">
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">Регистрация</h2>
        <p class="text-gray-600 mb-8">Создайте аккаунт для доступа к льготам</p>

        <!-- Error Message -->
        <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-red-800 text-sm">{{ error }}</p>
        </div>

        <!-- Success Message -->
        <div v-if="success" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p class="text-green-800 text-sm">Регистрация успешна! Перенаправление...</p>
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
            <span class="px-2 bg-white text-gray-500">или зарегистрируйтесь по email</span>
          </div>
        </div>

        <!-- Registration Form -->
        <form @submit.prevent="handleRegister" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Имя пользователя</label>
            <input
              v-model="form.username"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="ivan_ivanov"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="example@mail.ru"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
            <input
              v-model="form.phone"
              type="tel"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="+7 (999) 123-45-67"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Категория льготника</label>
            <select
              v-model="form.beneficiary_category"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">Выберите категорию</option>
              <option value="pensioner">Пенсионер</option>
              <option value="disability_1">Инвалидность 1 группы</option>
              <option value="disability_2">Инвалидность 2 группы</option>
              <option value="disability_3">Инвалидность 3 группы</option>
              <option value="large_family">Многодетная семья</option>
              <option value="veteran">Ветеран</option>
              <option value="low_income">Малоимущий</option>
              <option value="svo_participant">Участник СВО</option>
              <option value="svo_family">Семья участника СВО</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Регион проживания</label>
            <input
              v-model="form.region"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Республика Саха (Якутия)"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">СНИЛС (необязательно)</label>
            <input
              v-model="form.snils"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="123-456-789 00"
              pattern="\d{3}-\d{3}-\d{3} \d{2}"
            />
            <p class="mt-1 text-xs text-gray-500">Формат: XXX-XXX-XXX XX</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Пароль</label>
            <input
              v-model="form.password"
              type="password"
              required
              minlength="6"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Минимум 6 символов"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Подтвердите пароль</label>
            <input
              v-model="form.password2"
              type="password"
              required
              minlength="6"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Повторите пароль"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-50"
          >
            {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
          </button>
        </form>

        <p class="mt-6 text-center text-sm text-gray-600">
          Уже есть аккаунт?
          <NuxtLink to="/login" class="text-primary-600 hover:text-primary-700 font-semibold">
            Войти
          </NuxtLink>
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
  username: '',
  email: '',
  phone: '',
  beneficiary_category: '',
  region: '',
  snils: '',
  password: '',
  password2: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

const toggleTheme = () => {
  const newTheme = settings.value.theme === 'light' ? 'dark' : 'light'
  updateSetting('theme', newTheme)
}

const handleRegister = async () => {
  error.value = ''

  if (form.value.password !== form.value.password2) {
    error.value = 'Пароли не совпадают'
    return
  }

  loading.value = true

  try {
    const response = await $fetch(`${config.public.apiBase}/auth/register/`, {
      method: 'POST',
      body: form.value
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
    error.value = err.data?.message || err.data?.email?.[0] || err.data?.username?.[0] || 'Ошибка регистрации. Проверьте данные.'
    loading.value = false
  }
}

const loginWithGosuslugi = async () => {
  loading.value = true
  error.value = ''

  // Mock Gosuslugi OAuth flow
  const mockEmail = prompt('Введите email для Госуслуг (это демо):')

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
  title: 'Регистрация | ПОДДЕРЖКА+',
  meta: [
    { name: 'description', content: 'Зарегистрируйтесь для доступа к льготам и скидкам' }
  ]
})
</script>
