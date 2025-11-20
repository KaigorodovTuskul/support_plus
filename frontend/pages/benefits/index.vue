<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader :username="user?.username || 'Пользователь'" />

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Page Title and Filters -->
      <div class="mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-6">Доступные льготы</h2>

        <!-- Filters -->
        <div class="bg-white rounded-xl shadow p-6 mb-6">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <!-- Search -->
            <div class="md:col-span-3">
              <label class="block text-sm font-medium text-gray-700 mb-2">Поиск</label>
              <input
                v-model="filters.search"
                type="text"
                placeholder="Поиск по названию или описанию..."
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                @input="applyFilters"
              />
            </div>

            <!-- Benefit Type -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Тип льготы</label>
              <select
                v-model="filters.benefit_type"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                @change="applyFilters"
              >
                <option value="">Все типы</option>
                <option value="federal">Федеральные</option>
                <option value="regional">Региональные</option>
                <option value="municipal">Муниципальные</option>
              </select>
            </div>

            <!-- Category -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Категория</label>
              <select
                v-model="filters.category"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                @change="applyFilters"
              >
                <option value="">Все категории</option>
                <option value="pensioner">Пенсионеры</option>
                <option value="disability_1">Инвалидность 1 группы</option>
                <option value="disability_2">Инвалидность 2 группы</option>
                <option value="disability_3">Инвалидность 3 группы</option>
                <option value="large_family">Многодетные семьи</option>
                <option value="veteran">Ветераны</option>
                <option value="low_income">Малоимущие</option>
                <option value="svo_participant">Участники СВО</option>
                <option value="svo_family">Семьи участников СВО</option>
              </select>
            </div>

            <!-- Region -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">Регион</label>
              <select
                v-model="filters.region"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                @change="applyFilters"
              >
                <option value="">Все регионы</option>
                <option value="Москва">Москва</option>
                <option value="Санкт-Петербург">Санкт-Петербург</option>
                <option value="Московская область">Московская область</option>
                <option value="Республика Саха (Якутия)">Республика Саха (Якутия)</option>
              </select>
            </div>
          </div>

          <div class="mt-4 flex justify-between items-center">
            <div class="flex space-x-3">
              <button
                v-if="showingAllBenefits"
                @click="resetFilters"
                class="text-primary-600 hover:text-primary-700 font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-3 py-1"
              >
                Показать только мои льготы
              </button>
              <button
                v-else
                @click="showAllBenefits"
                class="text-primary-600 hover:text-primary-700 font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-3 py-1"
              >
                Показать все льготы
              </button>
              <button
                @click="resetFilters"
                class="text-gray-600 hover:text-gray-900 font-semibold focus:outline-none focus:ring-2 focus:ring-primary-500 rounded px-3 py-1"
              >
                Сбросить фильтры
              </button>
            </div>
            <p class="text-sm text-gray-600">
              <span v-if="!showingAllBenefits" class="text-primary-600 font-semibold">Ваши льготы: </span>
              <strong>{{ filteredBenefits.length }}</strong> {{ getBenefitsWord(filteredBenefits.length) }}
            </p>
          </div>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="text-gray-600 mt-4">Загрузка льгот...</p>
      </div>

      <!-- Benefits List -->
      <div v-else-if="filteredBenefits.length > 0" class="grid grid-cols-1 gap-6">
        <div
          v-for="benefit in filteredBenefits"
          :key="benefit.id"
          class="bg-white rounded-xl shadow hover:shadow-lg transition p-6"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <!-- Type Badge -->
              <div class="flex items-center space-x-2 mb-3">
                <span
                  class="px-3 py-1 text-xs font-semibold rounded-full"
                  :class="{
                    'bg-blue-100 text-blue-800': benefit.benefit_type === 'federal',
                    'bg-green-100 text-green-800': benefit.benefit_type === 'regional',
                    'bg-purple-100 text-purple-800': benefit.benefit_type === 'municipal'
                  }"
                >
                  {{ getBenefitTypeName(benefit.benefit_type) }}
                </span>
                <span
                  v-if="benefit.is_active"
                  class="px-3 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800"
                >
                  Активна
                </span>
                <span
                  v-else
                  class="px-3 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800"
                >
                  Неактивна
                </span>
              </div>

              <!-- Title -->
              <h3 class="text-xl font-bold text-gray-900 mb-2">{{ benefit.title }}</h3>

              <!-- Description -->
              <p class="text-gray-600 mb-4">{{ benefit.description }}</p>

              <!-- Details -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <!-- Categories -->
                <div v-if="benefit.target_groups && benefit.target_groups.length > 0">
                  <span class="font-semibold text-gray-700">Категории:</span>
                  <div class="flex flex-wrap gap-1 mt-1">
                    <span
                      v-for="category in benefit.target_groups.slice(0, 3)"
                      :key="category"
                      class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      {{ getCategoryName(category) }}
                    </span>
                    <span
                      v-if="benefit.target_groups.length > 3"
                      class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      +{{ benefit.target_groups.length - 3 }}
                    </span>
                  </div>
                </div>

                <!-- Regions -->
                <div v-if="benefit.regions && benefit.regions.length > 0">
                  <span class="font-semibold text-gray-700">Регионы:</span>
                  <div class="flex flex-wrap gap-1 mt-1">
                    <span
                      v-for="region in benefit.regions.slice(0, 2)"
                      :key="region.id"
                      class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      {{ region.name }}
                    </span>
                    <span
                      v-if="benefit.regions.length > 2"
                      class="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      +{{ benefit.regions.length - 2 }}
                    </span>
                  </div>
                </div>

                <!-- Valid Period -->
                <div>
                  <span class="font-semibold text-gray-700">Период действия:</span>
                  <p class="text-gray-600">
                    {{ formatDate(benefit.valid_from) }} - {{ formatDate(benefit.valid_to) }}
                  </p>
                </div>

                <!-- Application Method -->
                <div v-if="benefit.application_method">
                  <span class="font-semibold text-gray-700">Способ получения:</span>
                  <p class="text-gray-600">{{ benefit.application_method }}</p>
                </div>
              </div>

              <!-- Required Documents -->
              <div v-if="benefit.required_documents && benefit.required_documents.length > 0" class="mt-4">
                <span class="font-semibold text-gray-700 text-sm">Необходимые документы:</span>
                <ul class="list-disc list-inside text-gray-600 text-sm mt-1">
                  <li v-for="doc in benefit.required_documents.slice(0, 3)" :key="doc">{{ doc }}</li>
                  <li v-if="benefit.required_documents.length > 3" class="text-primary-600 font-semibold">
                    +{{ benefit.required_documents.length - 3 }} ещё...
                  </li>
                </ul>
              </div>
            </div>

            <!-- Action Button -->
            <div class="ml-6">
              <NuxtLink
                :to="`/benefits/${benefit.id}`"
                class="px-6 py-3 bg-primary-600 text-white rounded-lg text-sm font-semibold hover:bg-primary-700 transition focus:outline-none focus:ring-2 focus:ring-primary-500 whitespace-nowrap"
              >
                Подробнее
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">Льготы не найдены</h3>
        <p class="mt-1 text-sm text-gray-500">Попробуйте изменить фильтры поиска</p>
        <div class="mt-6">
          <button
            @click="resetFilters"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            Сбросить фильтры
          </button>
        </div>
      </div>
    </main>

    <!-- Floating Chatbot -->
    <Chatbot />
  </div>
</template>

<script setup>
const router = useRouter()
const config = useRuntimeConfig()

const user = ref(null)
const benefits = ref([])
const filteredBenefits = ref([])
const loading = ref(true)

const filters = ref({
  search: '',
  benefit_type: '',
  category: '',
  region: ''
})

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

  // Fetch benefits - by default show personalized benefits
  try {
    console.log('Fetching benefits...')
    const response = await $fetch(`${config.public.apiBase}/benefits/?personalized=true`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    console.log('Benefits response:', response)
    console.log('Response type:', typeof response)
    console.log('Is array:', Array.isArray(response))

    // Check if response is paginated (has 'results' key) or direct array
    if (response && typeof response === 'object' && 'results' in response) {
      console.log('Paginated response, results count:', response.results.length)
      benefits.value = response.results
    } else if (Array.isArray(response)) {
      console.log('Direct array response, count:', response.length)
      benefits.value = response
    } else {
      console.error('Unexpected response format:', response)
      benefits.value = []
    }

    filteredBenefits.value = benefits.value
    console.log('Benefits loaded:', benefits.value.length)
  } catch (err) {
    console.error('Error loading benefits:', err)
    console.error('Error details:', err.data)
  } finally {
    loading.value = false
  }
})

// Flag to track if showing all benefits
const showingAllBenefits = ref(false)

const applyFilters = () => {
  let result = [...benefits.value]

  // Search filter
  if (filters.value.search) {
    const searchLower = filters.value.search.toLowerCase()
    result = result.filter(b =>
      b.title.toLowerCase().includes(searchLower) ||
      b.description.toLowerCase().includes(searchLower)
    )
  }

  // Benefit type filter
  if (filters.value.benefit_type) {
    result = result.filter(b => b.benefit_type === filters.value.benefit_type)
  }

  // Category filter
  if (filters.value.category) {
    result = result.filter(b =>
      b.target_groups && b.target_groups.includes(filters.value.category)
    )
  }

  // Region filter
  if (filters.value.region) {
    result = result.filter(b =>
      b.regions && b.regions.some(r => r.name === filters.value.region)
    )
  }

  filteredBenefits.value = result
}

const resetFilters = async () => {
  filters.value = {
    search: '',
    benefit_type: '',
    category: '',
    region: ''
  }

  // If showing all benefits, switch back to personalized
  if (showingAllBenefits.value) {
    loading.value = true
    try {
      const token = localStorage.getItem('access_token')
      const response = await $fetch(`${config.public.apiBase}/benefits/?personalized=true`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      })

      // Handle paginated response
      if (response && typeof response === 'object' && 'results' in response) {
        benefits.value = response.results
      } else if (Array.isArray(response)) {
        benefits.value = response
      } else {
        benefits.value = []
      }

      showingAllBenefits.value = false
    } catch (err) {
      console.error('Error loading personalized benefits:', err)
    } finally {
      loading.value = false
    }
  }

  filteredBenefits.value = benefits.value
}

const showAllBenefits = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await $fetch(`${config.public.apiBase}/benefits/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    // Handle paginated response
    if (response && typeof response === 'object' && 'results' in response) {
      benefits.value = response.results
    } else if (Array.isArray(response)) {
      benefits.value = response
    } else {
      benefits.value = []
    }

    showingAllBenefits.value = true
    filteredBenefits.value = benefits.value
  } catch (err) {
    console.error('Error loading all benefits:', err)
  } finally {
    loading.value = false
  }
}

const getBenefitTypeName = (type) => {
  const names = {
    'federal': 'Федеральная',
    'regional': 'Региональная',
    'municipal': 'Муниципальная'
  }
  return names[type] || type
}

const getCategoryName = (category) => {
  const names = {
    'pensioner': 'Пенсионер',
    'disability_1': 'Инвалидность 1 группы',
    'disability_2': 'Инвалидность 2 группы',
    'disability_3': 'Инвалидность 3 группы',
    'large_family': 'Многодетная семья',
    'veteran': 'Ветеран',
    'low_income': 'Малоимущий',
    'svo_participant': 'Участник СВО',
    'svo_family': 'Семья участника СВО'
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

const getBenefitsWord = (count) => {
  if (count % 10 === 1 && count % 100 !== 11) return 'льгота'
  if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) return 'льготы'
  return 'льгот'
}

useHead({
  title: 'Льготы | Опора',
  meta: [
    { name: 'description', content: 'Полный список доступных государственных льгот' }
  ]
})
</script>
