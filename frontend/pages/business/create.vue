<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />

    <main class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">Создать акцию</h1>
        <p class="text-xl text-gray-600">
          Разместите специальное предложение для пользователей платформы
        </p>
      </div>

      <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-800 text-sm">{{ error }}</p>
      </div>

      <div v-if="success" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-green-800 text-sm">Акция создана и отправлена на модерацию!</p>
      </div>

      <form @submit.prevent="handleSubmit" class="bg-white rounded-xl shadow-lg p-8 space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Название акции <span class="text-red-500">*</span>
          </label>
          <input
            v-model="form.title"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="Скидка 20% на все товары"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Описание <span class="text-red-500">*</span>
          </label>
          <textarea
            v-model="form.description"
            required
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="Подробное описание акции, условия получения скидки..."
          ></textarea>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Категория <span class="text-red-500">*</span>
            </label>
            <select
              v-model="form.category"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="">Выберите категорию</option>
              <option value="discount">Скидка</option>
              <option value="service">Услуга</option>
              <option value="product">Товар</option>
              <option value="event">Мероприятие</option>
              <option value="other">Другое</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Процент скидки
            </label>
            <input
              v-model.number="form.discount_percentage"
              type="number"
              min="0"
              max="100"
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="10"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Действует с <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.valid_from"
              type="date"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Действует до <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.valid_until"
              type="date"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Телефон для связи
          </label>
          <input
            v-model="form.contact_phone"
            type="tel"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="+7 (999) 123-45-67"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Email для связи
          </label>
          <input
            v-model="form.contact_email"
            type="email"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="info@example.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Сайт компании
          </label>
          <input
            v-model="form.website_url"
            type="url"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="https://example.com"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            URL логотипа компании
          </label>
          <input
            v-model="form.company_logo_url"
            type="url"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="https://example.com/logo.png"
          />
        </div>

        <div class="flex space-x-4">
          <button
            type="submit"
            :disabled="loading"
            class="flex-1 py-3 px-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-50"
          >
            {{ loading ? 'Создание...' : 'Создать акцию' }}
          </button>
          <NuxtLink
            to="/business/my-offers"
            class="flex-1 py-3 px-4 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition text-center"
          >
            Отменить
          </NuxtLink>
        </div>
      </form>
    </main>
  </div>
</template>

<script setup>
const config = useRuntimeConfig()
const router = useRouter()

const form = ref({
  title: '',
  description: '',
  category: '',
  discount_percentage: null,
  valid_from: '',
  valid_until: '',
  contact_phone: '',
  contact_email: '',
  website_url: '',
  company_logo_url: ''
})

const loading = ref(false)
const error = ref('')
const success = ref(false)

onMounted(() => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/login')
  }
})

const handleSubmit = async () => {
  error.value = ''
  loading.value = true

  try {
    const token = localStorage.getItem('access_token')
    await $fetch(`${config.public.apiBase}/business/offers/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: form.value
    })

    success.value = true

    setTimeout(() => {
      router.push('/business/my-offers')
    }, 2000)
  } catch (err) {
    error.value = err.data?.message || 'Ошибка при создании акции. Попробуйте еще раз.'
    loading.value = false
  }
}

useHead({
  title: 'Создать акцию | Опора'
})
</script>
