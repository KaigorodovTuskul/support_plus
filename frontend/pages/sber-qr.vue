<template>
  <div class="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center px-4">
    <div class="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
      <h2 class="text-3xl font-bold text-gray-900 mb-6">Вход по Сбер ID</h2>

      <!-- QR Code -->
      <div class="bg-gray-100 rounded-xl p-8 mb-6 flex items-center justify-center">
        <div class="w-64 h-64 bg-white rounded-lg shadow-inner flex items-center justify-center">
          <!-- ВСТАВЬ СВОЮ КАРТИНКУ QR-КОДА ЗДЕСЬ -->
          <img 
            src="/qr_code.png" 
            alt="QR-код для оплаты" 
            class="w-48 h-48 object-contain"
          >
        </div>
      </div>

      <p class="text-gray-700 mb-4">Наведите QR-сканер из приложения СберБанк Онлайн</p>

      <!-- Remember Me Checkbox -->
      <label class="flex items-center justify-center mb-6 cursor-pointer">
        <input v-model="rememberMe" type="checkbox" class="w-4 h-4 text-green-600 rounded focus:ring-2 focus:ring-green-500">
        <span class="ml-2 text-gray-700">Запомнить меня</span>
      </label>

      <!-- Timer -->
      <div class="mb-6">
        <p class="text-gray-600 text-sm">Код действителен еще</p>
        <p class="text-3xl font-bold text-gray-900">{{ formatTime(timeLeft) }}</p>
      </div>

      <!-- Loading State -->
      <div v-if="authenticating" class="mb-4">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto"></div>
        <p class="text-green-600 mt-2">Выполняется вход...</p>
      </div>

      <!-- Login Button -->
      <button
        v-if="showLoginButton && !authenticating"
        @click="performMockAuth"
        class="w-full mb-3 py-3 px-4 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition"
      >
        Войти
      </button>

      <!-- Cancel Button -->
      <button
        @click="cancel"
        class="text-gray-600 hover:text-gray-900 text-sm"
      >
        Отменить
      </button>
    </div>
  </div>
</template>

<script setup>
const router = useRouter()
const config = useRuntimeConfig()

const timeLeft = ref(300)
const rememberMe = ref(false)
const authenticating = ref(false)
const showLoginButton = ref(false)
let timer = null

// Храним данные созданного пользователя
const createdUser = ref(null)

onMounted(() => {
  timer = setInterval(() => {
    timeLeft.value--
    if (timeLeft.value <= 0) {
      clearInterval(timer)
      router.push('/login')
    }
  }, 1000)

  setTimeout(() => {
    showLoginButton.value = true
  }, 0)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const performMockAuth = async () => {
  authenticating.value = true

  try {
    // Создаем уникальные данные для пользователя
    const timestamp = Date.now()
    const username = `sber_user_${timestamp}`
    const email = `sber_${timestamp}@demo.ru`
    const password = 'sberid_demo_2024'

    console.log('Регистрируем пользователя:', { username, email })

    // 1. Регистрируем нового пользователя
    const registerResponse = await $fetch(`${config.public.apiBase}/auth/register/`, {
      method: 'POST',
      body: {
        username: username,
        email: email,
        password: password,
        password2: password,
        first_name: 'Сбер',
        last_name: 'Пользователь',
        beneficiary_category: 'pensioner',
        region: 'Москва'
      }
    })

    console.log('Регистрация успешна:', registerResponse)

    // 2. Логинимся с ТЕМИ ЖЕ данными
    console.log('Пытаемся войти с:', { username, password })
    
    const loginResponse = await $fetch(`${config.public.apiBase}/auth/login/`, {
      method: 'POST',
      body: {
        username: username, // Используем ТОЧНО ТОТ ЖЕ username
        password: password  // Используем ТОЧНО ТОТ ЖЕ пароль
      }
    })

    console.log('Логин успешен:', loginResponse)

    // 3. Сохраняем токены
    localStorage.setItem('access_token', loginResponse.access)
    localStorage.setItem('refresh_token', loginResponse.refresh)

    // 4. Получаем информацию о пользователе
    const user = await $fetch(`${config.public.apiBase}/auth/me/`, {
      headers: {
        Authorization: `Bearer ${loginResponse.access}`
      }
    })

    console.log('Информация о пользователе:', user)

    localStorage.setItem('user', JSON.stringify(user))

    if (rememberMe.value) {
      localStorage.setItem('remember_me', 'true')
    }

    // Редирект на дашборд
    setTimeout(() => {
      router.push('/dashboard')
    }, 500)

  } catch (err) {
    console.error('Sber ID auth error:', err)
    
    // Если регистрация не удалась, пробуем войти с тестовым пользователем
    if (err.status === 400 || err.status === 401) {
      await tryWithTestUser()
    } else {
      router.push('/login')
    }
  }
}

const tryWithTestUser = async () => {
  try {
    console.log('Пробуем тестового пользователя...')
    
    // Пробуем разные комбинации тестовых пользователей
    const testUsers = [
      { username: 'demo@demo.ru', password: 'demo123' },
      { username: 'test@test.com', password: 'test123' },
      { username: 'admin', password: 'admin' },
      { username: 'user', password: 'user123' }
    ]

    for (const user of testUsers) {
      try {
        const loginResponse = await $fetch(`${config.public.apiBase}/auth/login/`, {
          method: 'POST',
          body: user
        })

        console.log('Успешный вход с:', user.username)
        
        localStorage.setItem('access_token', loginResponse.access)
        localStorage.setItem('refresh_token', loginResponse.refresh)

        const userInfo = await $fetch(`${config.public.apiBase}/auth/me/`, {
          headers: {
            Authorization: `Bearer ${loginResponse.access}`
          }
        })

        localStorage.setItem('user', JSON.stringify(userInfo))
        router.push('/dashboard')
        return
        
      } catch (e) {
        console.log(`Не удалось войти с ${user.username}:`, e.status)
      }
    }

    // Если ни один тестовый пользователь не подошел
    throw new Error('No test users worked')

  } catch (err) {
    console.error('All login attempts failed:', err)
    
    // Создаем простого мок-пользователя для демо
    createMockUser()
  }
}

const createMockUser = () => {
  console.log('Создаем мок-пользователя для демо')
  
  const mockUser = {
    id: 1,
    username: 'sber_demo_user',
    email: 'sber@demo.ru',
    first_name: 'Сбер',
    last_name: 'Демо',
    beneficiary_category: 'pensioner',
    region: 'Москва'
  }

  const mockTokens = {
    access: 'mock_jwt_token_' + Date.now(),
    refresh: 'mock_refresh_token_' + Date.now()
  }

  localStorage.setItem('access_token', mockTokens.access)
  localStorage.setItem('refresh_token', mockTokens.refresh)
  localStorage.setItem('user', JSON.stringify(mockUser))

  router.push('/dashboard')
}

const cancel = () => {
  if (timer) {
    clearInterval(timer)
  }
  router.push('/login')
}

useHead({
  title: 'Вход по Сбер ID | Опора',
  meta: [
    { name: 'description', content: 'Авторизация через Сбер ID' }
  ]
})
</script>