<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader />

    <!-- Main Content -->
    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <!-- Thank You Message -->
      <div class="bg-white rounded-xl shadow-lg p-8 mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">Спасибо за вашу поддержку!</h1>
        <p class="text-gray-600 mb-4">
          Ваша помощь помогает проекту "Опора" продолжать работу по поддержке людей с ограниченными возможностями,
          пожилых людей и других категорий граждан, нуждающихся в социальной поддержке.
        </p>
        <p class="text-gray-600">
          Каждый рубль идет на развитие платформы, создание нового функционала и помощь тем, кто в ней нуждается.
        </p>
      </div>

      <!-- Donation Form -->
      <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Сделать пожертвование</h2>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Amount (Required) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Сумма пожертвования <span class="text-red-500">*</span>
            </label>
            <div class="relative">
              <input
                v-model="form.amount"
                type="number"
                min="1"
                step="1"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Введите сумму"
              />
              <span class="absolute right-4 top-2 text-gray-500">₽</span>
            </div>
            <!-- Quick Amount Buttons -->
            <div class="grid grid-cols-4 gap-2 mt-3">
              <button
                v-for="amount in quickAmounts"
                :key="amount"
                type="button"
                @click="form.amount = amount"
                class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition text-sm"
              >
                {{ amount }} ₽
              </button>
            </div>
          </div>

          <!-- Donor Name (Optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Ваше имя
            </label>
            <input
              v-model="form.donor_name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Как вас зовут?"
            />
            <p class="text-xs text-gray-500 mt-1">
              Оставьте пустым для анонимного пожертвования
            </p>
          </div>

          <!-- Email (Optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              v-model="form.contact_email"
              type="email"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="your@email.com"
            />
            <p class="text-xs text-gray-500 mt-1">
              Для отправки квитанции для налогового вычета
            </p>
          </div>

          <!-- Phone (Optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Телефон
            </label>
            <input
              v-model="form.contact_phone"
              type="tel"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="+7 (___) ___-__-__"
            />
          </div>

          <!-- Message (Optional) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Сообщение
            </label>
            <textarea
              v-model="form.message"
              rows="3"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="Оставьте сообщение (по желанию)"
            ></textarea>
          </div>

          <!-- Show on Leaderboard -->
          <div class="flex items-center">
            <input
              v-model="form.show_on_leaderboard"
              type="checkbox"
              id="show_leaderboard"
              class="w-4 h-4 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
            />
            <label for="show_leaderboard" class="ml-2 text-sm text-gray-700">
              Показывать меня в списке благотворителей
            </label>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-50 flex items-center justify-center"
          >
            <span v-if="!loading">Перейти к оплате через СБП</span>
            <span v-else>Обработка...</span>
          </button>
        </form>
      </div>

      <!-- Info Block -->
      <div class="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 class="font-semibold text-blue-900 mb-2">Безопасная оплата</h3>
        <p class="text-sm text-blue-800">
          Все платежи обрабатываются через систему быстрых платежей (СБП).
          После подтверждения пожертвования вы получите квитанцию для налогового вычета.
        </p>
      </div>
    </main>

    <!-- Anonymous Confirmation Modal -->
    <div
      v-if="showAnonymousConfirm"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 class="text-xl font-bold text-gray-900 mb-4">Анонимное пожертвование</h3>
        <p class="text-gray-600 mb-6">
          Вы не заполнили данные о доноре. Пожертвование будет анонимным и не будет отображаться
          в списке благотворителей. Вы уверены, что хотите продолжить?
        </p>
        <div class="flex space-x-4">
          <button
            @click="confirmAnonymous"
            class="flex-1 py-2 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition"
          >
            Да, продолжить
          </button>
          <button
            @click="showAnonymousConfirm = false"
            class="flex-1 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
          >
            Заполнить данные
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const router = useRouter()
const config = useRuntimeConfig()

const form = ref({
  donor_type: 'individual',
  amount: null,
  donor_name: '',
  contact_email: '',
  contact_phone: '',
  message: '',
  show_on_leaderboard: true,
  is_anonymous: false
})

const quickAmounts = [500, 1000, 2500, 5000]
const loading = ref(false)
const showAnonymousConfirm = ref(false)

const handleSubmit = async () => {
  // Check if donation is anonymous
  const isAnonymous = !form.value.donor_name && !form.value.company_name

  if (isAnonymous && !form.value.is_anonymous) {
    // Show confirmation modal
    showAnonymousConfirm.value = true
    return
  }

  await processDonation()
}

const confirmAnonymous = () => {
  form.value.is_anonymous = true
  showAnonymousConfirm.value = false
  processDonation()
}

const processDonation = async () => {
  loading.value = true

  try {
    const response = await $fetch(`${config.public.apiBase}/donations/`, {
      method: 'POST',
      body: {
        donor_type: form.value.donor_type,
        amount: form.value.amount,
        donor_name: form.value.donor_name,
        company_name: form.value.company_name,
        company_address: form.value.company_address,
        contact_email: form.value.contact_email,
        contact_phone: form.value.contact_phone,
        message: form.value.message,
        show_on_leaderboard: form.value.show_on_leaderboard,
        is_anonymous: !form.value.donor_name && !form.value.company_name
      }
    })

    console.log('Донат создан в БД:', response)

    setTimeout(() => {
      router.push(`/donate/payment?txn=${response.transaction_id}&amount=${form.value.amount}`)
    }, 2000)

  } catch (err) {
    console.error('Error creating donation:', err)
    alert('Произошла ошибка. Попробуйте еще раз.')
    loading.value = false
  }
}

useHead({
  title: 'Помочь проекту - Частным лицам | Опора',
  meta: [
    { name: 'description', content: 'Сделайте пожертвование проекту Опора' }
  ]
})
</script>
