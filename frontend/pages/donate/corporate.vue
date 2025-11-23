<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Корпоративное партнерство</h1>
        <p class="text-xl text-gray-600">Ваша компания может сделать корпоративное пожертвование и стать:</p>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 border-2 border-yellow-300 rounded-xl p-6">
          <div class="text-center mb-4">
            <h3 class="text-2xl font-bold text-yellow-900 mb-2">Золотой партнер</h3>
            <p class="text-3xl font-bold text-yellow-700">100 000+ ₽</p>
          </div>
          <ul class="space-y-2 text-sm text-gray-700">
            <li>✓ Благодарность от проекта Опора</li>
            <li>✓ Новость в соцсетях</li>
            <li>✓ Логотип на главной странице</li>
            <li>✓ Информация в "Нам помогают"</li>
            <li>✓ Приглашение на мероприятия</li>
            <li>✓ Табличка в офисе</li>
            <li>✓ Корпоративное волонтерство</li>
            <li>✓ Бизнес-завтрак с партнерами</li>
            <li>✓ Упоминание в материалах</li>
          </ul>
        </div>
        <div class="bg-gradient-to-br from-gray-50 to-gray-100 border-2 border-gray-300 rounded-xl p-6">
          <div class="text-center mb-4">
            <h3 class="text-2xl font-bold text-gray-900 mb-2">Серебряный партнер</h3>
            <p class="text-3xl font-bold text-gray-700">50 000+ ₽</p>
          </div>
          <ul class="space-y-2 text-sm text-gray-700">
            <li>✓ Благодарность от проекта</li>
            <li>✓ Новость в соцсетях</li>
            <li>✓ Логотип в "Нам помогают"</li>
            <li>✓ Приглашение на мероприятия</li>
            <li>✓ Упоминание онлайн</li>
          </ul>
        </div>
        <div class="bg-gradient-to-br from-orange-50 to-orange-100 border-2 border-orange-300 rounded-xl p-6">
          <div class="text-center mb-4">
            <h3 class="text-2xl font-bold text-orange-900 mb-2">Бронзовый партнер</h3>
            <p class="text-3xl font-bold text-orange-700">25 000+ ₽</p>
          </div>
          <ul class="space-y-2 text-sm text-gray-700">
            <li>✓ Благодарность от проекта</li>
            <li>✓ Новость в соцсетях</li>
            <li>✓ Логотип в "Нам помогают"</li>
          </ul>
        </div>
      </div>
      <div class="bg-white rounded-xl shadow-lg p-8 max-w-3xl mx-auto">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Данные для пожертвования</h2>
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Сумма <span class="text-red-500">*</span></label>
            <input v-model="form.amount" type="number" min="1" required class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500" />
            <div class="grid grid-cols-3 gap-2 mt-2">
              <button v-for="amt in [25000, 50000, 100000]" :key="amt" type="button" @click="form.amount = amt" class="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm">{{ amt }} ₽</button>
            </div>
          </div>
          <div><label class="block text-sm font-medium text-gray-700 mb-1">Название компании</label><input v-model="form.company_name" type="text" class="w-full px-4 py-2 border rounded-lg" /></div>
          <div><label class="block text-sm font-medium text-gray-700 mb-1">Адрес компании</label><input v-model="form.company_address" type="text" class="w-full px-4 py-2 border rounded-lg" /></div>
          <div><label class="block text-sm font-medium text-gray-700 mb-1">Email</label><input v-model="form.contact_email" type="email" class="w-full px-4 py-2 border rounded-lg" /></div>
          <div><label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label><input v-model="form.contact_phone" type="tel" class="w-full px-4 py-2 border rounded-lg" /></div>
          <button type="submit" :disabled="loading" class="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700">Перейти к оплате</button>
        </form>
      </div>
    </main>
    <div v-if="showAnonymousConfirm" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4">Анонимное пожертвование</h3>
        <p class="text-gray-600 mb-6">Данные компании не заполнены. Продолжить?</p>
        <div class="flex space-x-4">
          <button @click="confirmAnonymous" class="flex-1 py-2 bg-primary-600 text-white rounded-lg">Да</button>
          <button @click="showAnonymousConfirm = false" class="flex-1 py-2 bg-gray-200 rounded-lg">Назад</button>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
const router = useRouter()
const config = useRuntimeConfig()
const form = ref({donor_type: 'company', amount: null, company_name: '', company_address: '', contact_email: '', contact_phone: '', message: '', show_on_leaderboard: true, is_anonymous: false})
const loading = ref(false)
const showAnonymousConfirm = ref(false)
const handleSubmit = async () => {
  const isAnonymous = !form.value.company_name
  if (isAnonymous && !form.value.is_anonymous) {
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
      body: form.value
    })

    console.log('Полный ответ от API:', response)
    
    // Генерируем свой transaction_id если API не возвращает
    const transactionId = response.transaction_id || response.id || `txn_${Date.now()}`
    console.log('Используем transaction_id:', transactionId)
    
    setTimeout(() => {
      router.push(`/donate/payment?txn=${transactionId}&amount=${form.value.amount}`)
    }, 2000)

  } catch (err) {
    console.error('Error creating donation:', err)
    alert('Произошла ошибка. Попробуйте еще раз.')
    loading.value = false
  }
}
useHead({title: 'Корпоративное партнерство | Опора'})
</script>
