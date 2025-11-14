<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader :show-back-button="true" :show-user="false" :show-logout="false" />

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white rounded-2xl shadow-xl p-6 md:p-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-3xl font-bold text-gray-900">Настройки доступности</h2>
          <button
            @click="resetSettings"
            class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            Сбросить по умолчанию
          </button>
        </div>

        <div class="space-y-8">
          <!-- Theme Toggle -->
          <div class="border-b border-gray-200 pb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Тема оформления</h3>
            <div class="flex items-center space-x-4">
              <button
                @click="updateSetting('theme', 'light')"
                :class="[
                  'flex-1 py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.theme === 'light'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Светлая тема
              </button>
              <button
                @click="updateSetting('theme', 'dark')"
                :class="[
                  'flex-1 py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.theme === 'dark'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Темная тема
              </button>
            </div>
          </div>

          <!-- Font Size -->
          <div class="border-b border-gray-200 pb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Размер шрифта</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                @click="updateSetting('fontSize', 'normal')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.fontSize === 'normal'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Обычный
              </button>
              <button
                @click="updateSetting('fontSize', 'enlarged')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.fontSize === 'enlarged'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Увеличенный
              </button>
              <button
                @click="updateSetting('fontSize', 'huge')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.fontSize === 'huge'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Огромный
              </button>
            </div>
          </div>

          <!-- Font Family -->
          <div class="border-b border-gray-200 pb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Тип шрифта</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                @click="updateSetting('fontFamily', 'sans-serif')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.fontFamily === 'sans-serif'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Без засечек (Sans-serif)
              </button>
              <button
                @click="updateSetting('fontFamily', 'serif')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.fontFamily === 'serif'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                С засечками (Serif)
              </button>
            </div>
          </div>

          <!-- Letter Spacing -->
          <div class="border-b border-gray-200 pb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Межбуквенный интервал</h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                @click="updateSetting('letterSpacing', 'normal')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.letterSpacing === 'normal'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Обычный
              </button>
              <button
                @click="updateSetting('letterSpacing', 'enlarged')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.letterSpacing === 'enlarged'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Увеличенный
              </button>
              <button
                @click="updateSetting('letterSpacing', 'huge')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.letterSpacing === 'huge'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Огромный
              </button>
            </div>
          </div>

          <!-- Color Mode -->
          <div class="border-b border-gray-200 pb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Цветовой режим</h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                @click="updateSetting('colorMode', 'default')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.colorMode === 'default'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Обычный
              </button>
              <button
                @click="updateSetting('colorMode', 'monochrome')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.colorMode === 'monochrome'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Монохромный
              </button>
              <button
                @click="updateSetting('colorMode', 'inverted')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.colorMode === 'inverted'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Инвертированный
              </button>
              <button
                @click="updateSetting('colorMode', 'blue-bg')"
                :class="[
                  'py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.colorMode === 'blue-bg'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Синий фон
              </button>
            </div>
          </div>

          <!-- Image Display -->
          <div class="border-b border-gray-200 pb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Отображение изображений</h3>
            <div class="flex items-center space-x-4">
              <button
                @click="updateSetting('showImages', true)"
                :class="[
                  'flex-1 py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  settings.showImages
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Включено
              </button>
              <button
                @click="updateSetting('showImages', false)"
                :class="[
                  'flex-1 py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                  !settings.showImages
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                ]"
              >
                Выключено
              </button>
            </div>
          </div>

          <!-- Speech Assistant -->
          <div class="pb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Голосовой ассистент</h3>
            <div class="space-y-4">
              <div class="flex items-center space-x-4">
                <button
                  @click="updateSetting('speechAssistant', true)"
                  :class="[
                    'flex-1 py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                    settings.speechAssistant
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  ]"
                >
                  Включен
                </button>
                <button
                  @click="updateSetting('speechAssistant', false)"
                  :class="[
                    'flex-1 py-3 px-4 rounded-lg font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500',
                    !settings.speechAssistant
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  ]"
                >
                  Выключен
                </button>
              </div>

              <!-- Speech Controls (UI Only) -->
              <div v-if="settings.speechAssistant" class="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div class="flex items-center justify-center space-x-3 mb-3">
                  <button
                    class="px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition focus:outline-none focus:ring-2 focus:ring-green-500 disabled:opacity-50"
                    disabled
                  >
                    ▶ Воспроизвести
                  </button>
                  <button
                    class="px-4 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition focus:outline-none focus:ring-2 focus:ring-red-500 disabled:opacity-50"
                    disabled
                  >
                    ■ Стоп
                  </button>
                  <button
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
                    disabled
                  >
                    ↻ Повторить
                  </button>
                </div>
                <p class="text-sm text-blue-800 text-center">
                  <strong>Совет:</strong> Выделите текст и нажмите <kbd class="px-2 py-1 bg-white border border-blue-300 rounded text-xs">Ctrl+Enter</kbd> для озвучивания (функция будет добавлена позже)
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Info Box -->
      <div class="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h4 class="text-sm font-semibold text-blue-900 mb-2">О настройках доступности</h4>
        <p class="text-xs text-blue-800">
          Эти настройки помогают людям с различными потребностями комфортно использовать платформу. Все изменения сохраняются автоматически и применяются ко всем страницам сайта.
        </p>
      </div>
    </main>
  </div>
</template>

<script setup>
const router = useRouter()
const { settings, saveSettings, resetSettings: reset, updateSetting: update } = useAccessibility()

// Check authentication
onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/login')
  }
})

const resetSettings = () => {
  if (confirm('Вы уверены, что хотите сбросить все настройки доступности?')) {
    reset()
  }
}

const updateSetting = (key, value) => {
  update(key, value)
}

useHead({
  title: 'Настройки доступности | ПОДДЕРЖКА+',
  meta: [
    { name: 'description', content: 'Настройте параметры доступности для комфортного использования' }
  ]
})
</script>
