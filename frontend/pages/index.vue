<template>
  <div class="min-h-screen transition-colors duration-200" :class="settings.theme === 'dark' ? 'bg-gray-900' : 'bg-gradient-to-b from-green-50 to-white'">
    <!-- Header -->
    <header class="shadow-sm transition-colors duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <img src="/logo.jpg" alt="Опора" class="w-12 h-12 rounded-lg object-cover">
            <h1 class="text-2xl font-bold transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Опора</h1>
          </div>
          <nav class="flex items-center space-x-3">
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

            <NuxtLink to="/login" class="text-gray-600 hover:text-primary-600 transition font-semibold">
              Вход
            </NuxtLink>
            <NuxtLink to="/register" class="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500">
              Регистрация
            </NuxtLink>
          </nav>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center relative">
        <!-- Animated Robot -->
        <div class="absolute top-0 right-0 md:right-20 opacity-80 animate-bounce-slow">
          <img src="/roboto_128.gif" alt="Робот-помощник" class="w-32 h-32 md:w-48 md:h-48">
        </div>

        <h2 class="text-4xl font-bold mb-4 transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">
          Льготы и скидки в одном месте
        </h2>
        <p class="text-xl mb-8 max-w-3xl mx-auto transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'">
          Доступ к государственным льготам и коммерческим предложениям для пенсионеров,
          инвалидов, многодетных семей и других льготных категорий граждан
        </p>
        <div class="flex justify-center space-x-4">
          <NuxtLink to="/register" class="bg-primary-600 text-white px-8 py-3 rounded-lg text-lg font-semibold hover:bg-primary-700 transition shadow-lg">
            Начать использовать
          </NuxtLink>
          <NuxtLink to="/benefits" class="bg-white text-primary-600 px-8 py-3 rounded-lg text-lg font-semibold hover:bg-gray-50 transition border-2 border-primary-600">
            Посмотреть льготы
          </NuxtLink>
        </div>
      </div>

      <!-- Features -->
      <div class="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8">
        <div class="p-6 rounded-xl shadow-md transition-colors duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold mb-2 transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Государственные льготы</h3>
          <p class="transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'">
            Федеральные, региональные и муниципальные льготы с подробными инструкциями по получению
          </p>
        </div>

        <div class="p-6 rounded-xl shadow-md transition-colors duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
          <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold mb-2 transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Скидки от партнеров</h3>
          <p class="transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'">
            Специальные предложения от аптек, магазинов, банков и других организаций
          </p>
        </div>

        <div class="p-6 rounded-xl shadow-md transition-colors duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
          <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
            <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
          <h3 class="text-xl font-bold mb-2 transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Доступность</h3>
          <p class="transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-gray-300' : 'text-gray-600'">
            Настройки шрифта, контрастности, голосовой помощник для людей с ограниченными возможностями
          </p>
        </div>
      </div>

      <!-- Statistics -->
      <div class="mt-20 bg-primary-600 rounded-2xl p-8 text-white">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <div class="text-4xl font-bold mb-2">11+</div>
            <div class="text-blue-100">Государственных льгот</div>
          </div>
          <div>
            <div class="text-4xl font-bold mb-2">9+</div>
            <div class="text-blue-100">Коммерческих предложений</div>
          </div>
          <div>
            <div class="text-4xl font-bold mb-2">100%</div>
            <div class="text-blue-100">Бесплатно</div>
          </div>
        </div>
      </div>

      <!-- Benefits Categories -->
      <div class="mt-20">
        <h3 class="text-3xl font-bold text-center mb-10 transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Категории льгот</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="p-4 rounded-lg shadow text-center hover:shadow-lg transition-all duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
            <div class="text-3xl mb-2">🚌</div>
            <div class="font-semibold transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Транспорт</div>
          </div>
          <div class="p-4 rounded-lg shadow text-center hover:shadow-lg transition-all duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
            <div class="text-3xl mb-2">💊</div>
            <div class="font-semibold transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Медицина</div>
          </div>
          <div class="p-4 rounded-lg shadow text-center hover:shadow-lg transition-all duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
            <div class="text-3xl mb-2">🏠</div>
            <div class="font-semibold transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">ЖКХ</div>
          </div>
          <div class="p-4 rounded-lg shadow text-center hover:shadow-lg transition-all duration-200" :class="settings.theme === 'dark' ? 'bg-gray-800' : 'bg-white'">
            <div class="text-3xl mb-2">💰</div>
            <div class="font-semibold transition-colors duration-200" :class="settings.theme === 'dark' ? 'text-white' : 'text-gray-900'">Выплаты</div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-white mt-20 py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p class="text-gray-400">
          © 2025 Опора. Платформа для доступа к льготам и скидкам.
        </p>
        <p class="text-gray-500 text-sm mt-2">
          Разработано для помощи льготным категориям граждан
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
const { settings, updateSetting } = useAccessibility()

const toggleTheme = () => {
  const newTheme = settings.value.theme === 'light' ? 'dark' : 'light'
  updateSetting('theme', newTheme)
}

useHead({
  title: 'Опора | Льготы и скидки для льготников',
  meta: [
    { name: 'description', content: 'Доступ к государственным льготам и коммерческим скидкам для пенсионеров, инвалидов, многодетных семей' }
  ]
})
</script>

<style scoped>
@keyframes bounce-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce-slow {
  animation: bounce-slow 3s ease-in-out infinite;
}
</style>
