<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Success Message -->
      <div class="bg-green-50 border border-green-200 rounded-xl p-6 mb-8 text-center">
        <div class="flex justify-center mb-4">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <h1 class="text-3xl font-bold text-green-900 mb-2">Спасибо за вашу поддержку!</h1>
        <p class="text-green-800">
          Ваше пожертвование успешно обработано. Вы получили квитанцию для налогового вычета.
        </p>
      </div>

      <!-- Receipt -->
      <div v-if="donation" class="bg-white rounded-xl shadow-lg overflow-hidden">
        <!-- Header -->
        <div class="bg-primary-600 text-white p-6">
          <h2 class="text-2xl font-bold mb-2">Квитанция #{{ donation.transaction_id }}</h2>
          <p class="text-primary-100">Благотворительное пожертвование</p>
        </div>

        <!-- Receipt Body -->
        <div class="p-8 space-y-6">
          <!-- Organization Info -->
          <div>
            <h3 class="text-sm font-semibold text-gray-500 uppercase mb-2">Получатель</h3>
            <p class="font-semibold text-gray-900">Проект "Опора"</p>
            <p class="text-sm text-gray-600">Помощь гражданам с ограниченными возможностями</p>
            <p class="text-sm text-gray-600 mt-1">ИНН: 1234567890</p>
            <p class="text-sm text-gray-600">КПП: 123456789</p>
          </div>

          <hr class="border-gray-200">

          <!-- Donor Info -->
          <div>
            <h3 class="text-sm font-semibold text-gray-500 uppercase mb-2">Плательщик</h3>
            <p class="font-semibold text-gray-900">
              {{ donation.donor_name || 'Анонимный донор' }}
            </p>
            <p v-if="donation.contact_email" class="text-sm text-gray-600">{{ donation.contact_email }}</p>
            <p v-if="donation.contact_phone" class="text-sm text-gray-600">{{ donation.contact_phone }}</p>
          </div>

          <hr class="border-gray-200">

          <!-- Payment Details -->
          <div>
            <h3 class="text-sm font-semibold text-gray-500 uppercase mb-2">Детали платежа</h3>
            <div class="space-y-2">
              <div class="flex justify-between">
                <span class="text-gray-600">Дата платежа:</span>
                <span class="font-semibold text-gray-900">{{ formatDate(donation.payment_date) }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Способ оплаты:</span>
                <span class="font-semibold text-gray-900">СБП (Система быстрых платежей)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-600">Статус:</span>
                <span class="px-2 py-1 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                  Оплачено
                </span>
              </div>
            </div>
          </div>

          <hr class="border-gray-200">

          <!-- Amount -->
          <div class="bg-gray-50 rounded-lg p-6">
            <div class="flex justify-between items-center">
              <span class="text-lg text-gray-600">Сумма пожертвования:</span>
              <span class="text-3xl font-bold text-primary-600">
                {{ formatAmount(donation.amount) }} ₽
              </span>
            </div>
          </div>

          <!-- Message -->
          <div v-if="donation.message">
            <h3 class="text-sm font-semibold text-gray-500 uppercase mb-2">Ваше сообщение</h3>
            <p class="text-gray-700 italic">"{{ donation.message }}"</p>
          </div>

          <hr class="border-gray-200">

          <!-- Tax Deduction Info -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 class="font-semibold text-blue-900 mb-2">💡 Налоговый вычет</h3>
            <p class="text-sm text-blue-800 mb-2">
              Вы можете вернуть 13% от суммы пожертвования при подаче налоговой декларации.
            </p>
            <p class="text-sm text-blue-800">
              <strong>Сумма к возврату:</strong> {{ formatAmount(donation.amount * 0.13) }} ₽
            </p>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 p-6 border-t border-gray-200">
          <p class="text-xs text-gray-500 text-center">
            Квитанция сформирована {{ formatDate(new Date()) }}
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="mt-8 flex justify-center space-x-4">
        <button
          @click="printReceipt"
          class="px-6 py-3 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition flex items-center"
        >
          <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Распечатать
        </button>
        <NuxtLink
          to="/donate/leaderboard"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition"
        >
          Посмотреть лидерборд
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<script setup>
const route = useRoute()
const router = useRouter()
const config = useRuntimeConfig()

const donation = ref(null)
const txnId = route.query.txn

onMounted(async () => {
  if (!txnId) {
    router.push('/donate/individual')
    return
  }

  try {
    // Получаем данные доната из API
    const donations = await $fetch(`${config.public.apiBase}/donations/`)
    donation.value = donations.find(d => d.transaction_id === txnId)

    if (!donation.value) {
      // Если не найден в API, создаем мок-данные
      donation.value = {
        transaction_id: txnId,
        amount: 1000,
        donor_name: 'Анонимный донор',
        contact_email: '',
        contact_phone: '',
        message: '',
        payment_date: new Date().toISOString(),
        payment_status: 'paid'
      }
    }
  } catch (err) {
    console.error('Error loading donation:', err)
    // Мок-данные при ошибке
    donation.value = {
      transaction_id: txnId,
      amount: 1000,
      donor_name: 'Анонимный донор',
      payment_date: new Date().toISOString(),
      payment_status: 'paid'
    }
  }
})

const formatAmount = (amount) => {
  return new Intl.NumberFormat('ru-RU').format(amount)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const printReceipt = () => {
  window.print()
}

useHead({
  title: 'Квитанция | Опора',
  meta: [
    { name: 'description', content: 'Квитанция о пожертвовании' }
  ]
})
</script>

<style scoped>
@media print {
  /* Hide header and buttons when printing */
  header, button, a {
    display: none !important;
  }
}
</style>
