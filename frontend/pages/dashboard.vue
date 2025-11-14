<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader :username="user?.username || 'Пользователь'" />

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Welcome Section -->
      <div class="bg-gradient-to-r from-primary-600 to-green-600 rounded-2xl p-8 text-white mb-8">
        <h2 class="text-3xl font-bold mb-2">Добро пожаловать, {{ user?.username }}!</h2>
        <p class="text-blue-100 mb-4">
          Категория: {{ getCategoryName(user?.beneficiary_category) }}
        </p>
        <p class="text-blue-100">
          Регион: {{ user?.region }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-600">Загрузка данных...</p>
      </div>

      <!-- Dashboard Stats -->
      <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div class="bg-white rounded-xl shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-sm">Доступных льгот</p>
              <p class="text-3xl font-bold text-gray-900">{{ dashboard?.active_count || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-sm">Скоро истекают</p>
              <p class="text-3xl font-bold text-gray-900">{{ dashboard?.expiring_count || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-xl shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-500 text-sm">Коммерческих предложений</p>
              <p class="text-3xl font-bold text-gray-900">{{ offers?.length || 0 }}</p>
            </div>
            <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Benefits -->
      <div class="bg-white rounded-xl shadow mb-8">
        <div class="p-6 border-b border-gray-200">
          <h3 class="text-xl font-bold text-gray-900">Ваши льготы</h3>
        </div>
        <div class="p-6">
          <div v-if="dashboard?.active_benefits?.length" class="space-y-4">
            <div
              v-for="benefit in dashboard.active_benefits"
              :key="benefit.id"
              class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center space-x-2 mb-2">
                    <span
                      class="px-2 py-1 text-xs font-semibold rounded"
                      :class="{
                        'bg-blue-100 text-blue-800': benefit.benefit_type === 'federal',
                        'bg-green-100 text-green-800': benefit.benefit_type === 'regional',
                        'bg-purple-100 text-purple-800': benefit.benefit_type === 'municipal'
                      }"
                    >
                      {{ benefit.benefit_type === 'federal' ? 'Федеральная' : benefit.benefit_type === 'regional' ? 'Региональная' : 'Муниципальная' }}
                    </span>
                  </div>
                  <h4 class="text-lg font-semibold text-gray-900 mb-1">{{ benefit.title }}</h4>
                  <p class="text-gray-600 text-sm mb-2">{{ benefit.description.substring(0, 150) }}...</p>
                  <p class="text-xs text-gray-500">
                    Действует до: {{ new Date(benefit.valid_to).toLocaleDateString('ru-RU') }}
                  </p>
                </div>
                <NuxtLink
                  :to="`/benefits/${benefit.id}`"
                  class="ml-4 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-semibold hover:bg-primary-700 transition"
                >
                  Подробнее
                </NuxtLink>
              </div>
            </div>
          </div>
          <p v-else class="text-gray-500 text-center py-8">
            Льготы не найдены
          </p>
        </div>
      </div>

      <!-- Quick Links -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <NuxtLink
          to="/benefits"
          class="bg-white rounded-xl shadow p-6 hover:shadow-lg transition"
        >
          <h3 class="text-lg font-bold text-gray-900 mb-2">Все льготы</h3>
          <p class="text-gray-600 text-sm">Просмотрите полный список доступных льгот</p>
        </NuxtLink>

        <NuxtLink
          to="/settings"
          class="bg-white rounded-xl shadow p-6 hover:shadow-lg transition"
        >
          <h3 class="text-lg font-bold text-gray-900 mb-2">Настройки</h3>
          <p class="text-gray-600 text-sm">Настройте доступность и персонализацию</p>
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<script setup>
const router = useRouter()
const config = useRuntimeConfig()

const user = ref(null)
const dashboard = ref(null)
const offers = ref([])
const loading = ref(true)

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

  // Fetch dashboard data
  try {
    dashboard.value = await $fetch(`${config.public.apiBase}/benefits/dashboard/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    // Fetch offers
    offers.value = await $fetch(`${config.public.apiBase}/offers/?personalized=true`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  } catch (err) {
    console.error('Error loading dashboard:', err)
  } finally {
    loading.value = false
  }
})

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

useHead({
  title: 'Личный кабинет | ПОДДЕРЖКА+',
  meta: [
    { name: 'description', content: 'Личный кабинет пользователя' }
  ]
})
</script>
