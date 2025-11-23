<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Мои акции</h1>
        <p class="text-xl text-gray-600">
          Управляйте вашими предложениями для пользователей платформы
        </p>
      </div>

      <div class="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
        <NuxtLink to="/business/create" class="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition inline-block">
          Создать новую акцию
        </NuxtLink>
      </div>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="text-gray-600 mt-4">Загрузка...</p>
      </div>

      <div v-else-if="offers.length > 0" class="bg-white rounded-xl shadow overflow-hidden">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Название</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Категория</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Статус</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Период</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Просмотры</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Клики</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="offer in offers" :key="offer.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ offer.title }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                  {{ getCategoryName(offer.category) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-semibold rounded-full" :class="{
                  'bg-green-100 text-green-800': offer.status === 'approved',
                  'bg-yellow-100 text-yellow-800': offer.status === 'pending',
                  'bg-red-100 text-red-800': offer.status === 'rejected',
                  'bg-gray-100 text-gray-800': offer.status === 'expired'
                }">
                  {{ getStatusName(offer.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(offer.valid_from) }} - {{ formatDate(offer.valid_until) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ offer.views_count }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ offer.clicks_count }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="text-center py-12 bg-white rounded-xl">
        <svg class="mx-auto h-24 w-24 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <p class="text-gray-500 mt-4 mb-6">У вас пока нет акций</p>
        <NuxtLink to="/business/create" class="px-6 py-2 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition inline-block">
          Создать первую акцию
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const router = useRouter()
const offers = ref([])
const loading = ref(true)

onMounted(async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/login')
    return
  }

  await loadOffers()
})

const loadOffers = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    offers.value = await $fetch(`${config.public.apiBase}/business/offers/?my_offers=true`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  } catch (err) {
    console.error('Error loading offers:', err)
    offers.value = []
  } finally {
    loading.value = false
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getCategoryName = (category) => {
  const names = {
    discount: 'Скидка',
    service: 'Услуга',
    product: 'Товар',
    event: 'Мероприятие',
    other: 'Другое'
  }
  return names[category] || category
}

const getStatusName = (status) => {
  const names = {
    pending: 'На модерации',
    approved: 'Одобрено',
    rejected: 'Отклонено',
    expired: 'Истекло'
  }
  return names[status] || status
}

useHead({
  title: 'Мои акции | Опора'
})
</script>
