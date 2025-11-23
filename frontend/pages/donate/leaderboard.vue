<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Title -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Нам помогают</h1>
        <p class="text-xl text-gray-600">
          Мы благодарим всех неравнодушных людей и компании, которые нам помогают!
        </p>
      </div>

      <!-- Statistics -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <p class="text-gray-500 text-sm mb-2">Всего собрано</p>
          <p class="text-3xl font-bold text-primary-600">
            {{ formatAmount(stats.total_amount) }} ₽
          </p>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <p class="text-gray-500 text-sm mb-2">Золотых партнеров</p>
          <p class="text-3xl font-bold text-yellow-600">{{ stats.gold_partners }}</p>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <p class="text-gray-500 text-sm mb-2">Серебряных партнеров</p>
          <p class="text-3xl font-bold text-gray-400">{{ stats.silver_partners }}</p>
        </div>
        <div class="bg-white rounded-xl shadow p-6 text-center">
          <p class="text-gray-500 text-sm mb-2">Бронзовых партнеров</p>
          <p class="text-3xl font-bold text-orange-600">{{ stats.bronze_partners }}</p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="text-gray-600 mt-4">Загрузка...</p>
      </div>

      <!-- Leaderboard -->
      <div v-else class="bg-white rounded-xl shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  #
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Донор
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Статус
                </th>
                <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сумма
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Дата
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="(donation, index) in donations"
                :key="index"
                class="hover:bg-gray-50 transition"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ index + 1 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div v-if="donation.logo_url" class="flex-shrink-0 h-10 w-10">
                      <img :src="donation.logo_url" alt="Logo" class="h-10 w-10 rounded-full object-cover">
                    </div>
                    <div :class="donation.logo_url ? 'ml-4' : ''">
                      <div class="text-sm font-medium text-gray-900">{{ donation.display_name }}</div>
                      <div v-if="donation.message" class="text-sm text-gray-500">{{ donation.message }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    v-if="donation.tier !== 'none'"
                    class="px-2 py-1 text-xs font-semibold rounded-full"
                    :class="{
                      'bg-yellow-100 text-yellow-800': donation.tier === 'gold',
                      'bg-gray-100 text-gray-800': donation.tier === 'silver',
                      'bg-orange-100 text-orange-800': donation.tier === 'bronze'
                    }"
                  >
                    {{ getTierName(donation.tier) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-semibold text-gray-900">
                  {{ formatAmount(donation.amount) }} ₽
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(donation.created_at) }}
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Empty State -->
          <div v-if="!loading && donations.length === 0" class="text-center py-12">
            <p class="text-gray-500">Пока нет пожертвований</p>
          </div>
        </div>
      </div>

      <!-- CTA -->
      <div class="mt-12 text-center">
        <p class="text-gray-600 mb-6">Хотите помочь проекту?</p>
        <div class="flex justify-center space-x-4">
          <NuxtLink
            to="/donate/individual"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition"
          >
            Стать донором
          </NuxtLink>
          <NuxtLink
            to="/donate/corporate"
            class="px-6 py-3 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition"
          >
            Корпоративное партнерство
          </NuxtLink>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()

const donations = ref([])
const stats = ref({
  total_amount: 0,
  total_donations: 0,
  gold_partners: 0,
  silver_partners: 0,
  bronze_partners: 0
})
const loading = ref(true)

onMounted(async () => {
  try {
    // Получаем данные из API
    donations.value = await $fetch(`${config.public.apiBase}/donations/leaderboard/`)
    stats.value = await $fetch(`${config.public.apiBase}/donations/stats/`)
  } catch (err) {
    console.error('Error loading leaderboard:', err)
    
    // Fallback на мок-данные если API недоступно
    donations.value = [
      {
        display_name: 'Иван Иванов',
        amount: 5000,
        tier: 'silver',
        message: 'Спасибо за вашу работу!',
        created_at: new Date().toISOString()
      },
      {
        display_name: 'ООО "Рога и копыта"',
        amount: 25000,
        tier: 'bronze', 
        message: 'Поддерживаем социальные проекты',
        created_at: new Date().toISOString()
      }
    ]
    
    stats.value = {
      total_amount: 30000,
      total_donations: 2,
      gold_partners: 0,
      silver_partners: 1,
      bronze_partners: 1
    }
  } finally {
    loading.value = false
  }
})

const formatAmount = (amount) => {
  return new Intl.NumberFormat('ru-RU').format(amount)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getTierName = (tier) => {
  const names = {
    gold: 'Золотой партнер',
    silver: 'Серебряный партнер',
    bronze: 'Бронзовый партнер'
  }
  return names[tier] || ''
}

useHead({
  title: 'Нам помогают | Опора',
  meta: [
    { name: 'description', content: 'Список благотворителей проекта Опора' }
  ]
})
</script>
