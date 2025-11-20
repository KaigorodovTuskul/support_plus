<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader :username="user?.username || 'Пользователь'" />

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Back Button -->
      <NuxtLink
        to="/benefits"
        class="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-2 py-1"
      >
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Назад к списку льгот
      </NuxtLink>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="text-gray-600 mt-4">Загрузка информации...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
        <svg class="mx-auto h-12 w-12 text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="text-lg font-semibold text-red-800 mb-2">Ошибка загрузки</h3>
        <p class="text-red-600">{{ error }}</p>
      </div>

      <!-- Benefit Details -->
      <div v-else-if="benefit" class="bg-white rounded-2xl shadow-xl overflow-hidden">
        <!-- Header Section -->
        <div class="bg-gradient-to-r from-primary-600 to-green-600 px-8 py-6 text-white">
          <div class="flex items-start justify-between mb-4">
            <div class="flex items-center space-x-3">
              <span
                class="px-3 py-1 text-sm font-semibold rounded-full bg-white bg-opacity-20"
              >
                {{ getBenefitTypeName(benefit.benefit_type) }}
              </span>
              <span
                v-if="benefit.is_active"
                class="px-3 py-1 text-sm font-semibold rounded-full bg-green-500 bg-opacity-90"
              >
                Активна
              </span>
              <span
                v-else
                class="px-3 py-1 text-sm font-semibold rounded-full bg-gray-500 bg-opacity-90"
              >
                Неактивна
              </span>
            </div>
          </div>
          <h1 class="text-3xl font-bold mb-3">{{ benefit.title }}</h1>
          <p class="text-blue-100 text-lg">{{ benefit.description }}</p>
        </div>

        <!-- Content Sections -->
        <div class="p-8 space-y-8">
          <!-- Eligibility -->
          <section v-if="benefit.target_groups && benefit.target_groups.length > 0">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Кому предназначена</h2>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="category in benefit.target_groups"
                :key="category"
                class="px-4 py-2 bg-blue-50 text-blue-800 rounded-lg font-semibold"
              >
                {{ getCategoryName(category) }}
              </span>
            </div>
          </section>

          <!-- Regions -->
          <section v-if="benefit.regions && benefit.regions.length > 0" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Регионы действия</h2>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="region in benefit.regions"
                :key="region.id"
                class="px-4 py-2 bg-green-50 text-green-800 rounded-lg font-semibold"
              >
                {{ region.name }}
              </span>
            </div>
          </section>

          <!-- Validity Period -->
          <section class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Период действия</h2>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600 mb-1">Начало действия</p>
                <p class="text-lg font-semibold text-gray-900">{{ formatDate(benefit.valid_from) }}</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4">
                <p class="text-sm text-gray-600 mb-1">Окончание действия</p>
                <p class="text-lg font-semibold text-gray-900">{{ formatDate(benefit.valid_to) }}</p>
              </div>
            </div>
          </section>

          <!-- Application Method -->
          <section v-if="benefit.application_method" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Как получить</h2>
            <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
              <p class="text-gray-800">{{ benefit.application_method }}</p>
            </div>
          </section>

          <!-- Required Documents -->
          <section v-if="benefit.required_documents && benefit.required_documents.length > 0" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Необходимые документы</h2>
            <ul class="space-y-2">
              <li
                v-for="(doc, index) in benefit.required_documents"
                :key="index"
                class="flex items-start"
              >
                <svg class="w-6 h-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-gray-700">{{ doc }}</span>
              </li>
            </ul>
          </section>

          <!-- Amount -->
          <section v-if="benefit.amount" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Размер льготы</h2>
            <div class="bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6">
              <p class="text-3xl font-bold text-green-700">{{ benefit.amount }}</p>
            </div>
          </section>

          <!-- Legal Basis -->
          <section v-if="benefit.legal_basis" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Правовая основа</h2>
            <div class="bg-gray-50 rounded-lg p-6">
              <p class="text-gray-700 text-sm">{{ benefit.legal_basis }}</p>
            </div>
          </section>

          <!-- Contact Information -->
          <section v-if="benefit.contact_info" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Контактная информация</h2>
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <p class="text-gray-800 whitespace-pre-line">{{ benefit.contact_info }}</p>
            </div>
          </section>

          <!-- Additional Info -->
          <section v-if="benefit.additional_info" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Дополнительная информация</h2>
            <div class="prose max-w-none text-gray-700">
              <p class="whitespace-pre-line">{{ benefit.additional_info }}</p>
            </div>
          </section>

          <!-- Official Link -->
          <section v-if="benefit.official_link" class="border-t border-gray-200 pt-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">Официальная информация</h2>
            <a
              :href="benefit.official_link"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              Перейти на официальный сайт
              <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </section>
        </div>

        <!-- Footer Actions -->
        <div class="bg-gray-50 px-8 py-6 border-t border-gray-200">
          <div class="flex flex-col sm:flex-row justify-between items-center space-y-4 sm:space-y-0">
            <p class="text-sm text-gray-600">
              Обновлено: {{ formatDate(benefit.updated_at) }}
            </p>
            <div class="flex space-x-3">
              <NuxtLink
                to="/benefits"
                class="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                Вернуться к списку
              </NuxtLink>
              <NuxtLink
                to="/dashboard"
                class="px-6 py-2 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                На главную
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Floating Chatbot -->
    <Chatbot />
  </div>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const user = ref(null)
const benefit = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  // Check if user is logged in
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/login')
    return
  }

  // Get user from localStorage
  const userData = localStorage.getItem('user')
  if (userData) {
    user.value = JSON.parse(userData)
  }

  // Fetch benefit details
  try {
    benefit.value = await $fetch(`${config.public.apiBase}/benefits/${route.params.id}/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  } catch (err) {
    console.error('Error loading benefit:', err)
    error.value = 'Не удалось загрузить информацию о льготе. Возможно, она не существует.'
  } finally {
    loading.value = false
  }
})

const getBenefitTypeName = (type) => {
  const names = {
    'federal': 'Федеральная льгота',
    'regional': 'Региональная льгота',
    'municipal': 'Муниципальная льгота'
  }
  return names[type] || type
}

const getCategoryName = (category) => {
  const names = {
    'pensioner': 'Пенсионеры',
    'disability_1': 'Инвалиды 1 группы',
    'disability_2': 'Инвалиды 2 группы',
    'disability_3': 'Инвалиды 3 группы',
    'large_family': 'Многодетные семьи',
    'veteran': 'Ветераны',
    'low_income': 'Малоимущие',
    'svo_participant': 'Участники СВО',
    'svo_family': 'Семьи участников СВО'
  }
  return names[category] || category
}

const formatDate = (dateString) => {
  if (!dateString) return 'Н/Д'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

useHead({
  title: () => benefit.value ? `${benefit.value.title} | Опора` : 'Льгота | Опора',
  meta: [
    { name: 'description', content: () => benefit.value?.description || 'Информация о льготе' }
  ]
})
</script>
