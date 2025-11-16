<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <AppHeader :username="user?.username || 'Пользователь'" />

    <!-- Main Content -->
    <main class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-8">Личный кабинет</h2>

      <!-- Error Message -->
      <div v-if="error" class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <p class="text-red-800 text-sm">{{ error }}</p>
      </div>

      <!-- Success Message -->
      <div v-if="success" class="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
        <p class="text-green-800 text-sm">{{ success }}</p>
      </div>

      <!-- Profile Information -->
      <div class="bg-white rounded-xl shadow mb-6">
        <div class="p-6 border-b border-gray-200">
          <h3 class="text-xl font-bold text-gray-900">Личная информация</h3>
        </div>
        <div class="p-6">
          <form @submit.prevent="updateProfile" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Имя пользователя</label>
                <input
                  v-model="form.username"
                  type="text"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="ivan_ivanov"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  v-model="form.email"
                  type="email"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="example@mail.ru"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
                <input
                  v-model="form.phone"
                  type="tel"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="+7 (999) 123-45-67"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Категория льготника</label>
                <select
                  v-model="form.beneficiary_category"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Выберите категорию</option>
                  <option value="pensioner">Пенсионер</option>
                  <option value="disability_1">Инвалидность 1 группы</option>
                  <option value="disability_2">Инвалидность 2 группы</option>
                  <option value="disability_3">Инвалидность 3 группы</option>
                  <option value="large_family">Многодетная семья</option>
                  <option value="veteran">Ветеран</option>
                  <option value="low_income">Малоимущий</option>
                  <option value="svo_participant">Участник СВО</option>
                  <option value="svo_family">Семья участника СВО</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Регион проживания</label>
                <select
                  v-model="form.region"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Выберите регион</option>
                  <option value="Республика Саха (Якутия)">Республика Саха (Якутия)</option>
                  <option value="Москва">Москва</option>
                  <option value="Санкт-Петербург">Санкт-Петербург</option>
                  <option value="Московская область">Московская область</option>
                  <option value="Ленинградская область">Ленинградская область</option>
                  <option value="Свердловская область">Свердловская область</option>
                  <option value="Новосибирская область">Новосибирская область</option>
                  <option value="Краснодарский край">Краснодарский край</option>
                  <option value="Республика Татарстан">Республика Татарстан</option>
                  <option value="Республика Башкортостан">Республика Башкортостан</option>
                  <option value="Другой регион">Другой регион</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">СНИЛС</label>
                <input
                  v-model="form.snils"
                  type="text"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="123-456-789 00"
                  pattern="\d{3}-\d{3}-\d{3} \d{2}"
                />
                <p class="mt-1 text-xs text-gray-500">Формат: XXX-XXX-XXX XX</p>
              </div>
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="w-full py-3 px-4 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition disabled:opacity-50"
            >
              {{ loading ? 'Сохранение...' : 'Сохранить изменения' }}
            </button>
          </form>
        </div>
      </div>

      <!-- Change Password -->
      <div class="bg-white rounded-xl shadow">
        <div class="p-6 border-b border-gray-200">
          <h3 class="text-xl font-bold text-gray-900">Изменить пароль</h3>
        </div>
        <div class="p-6">
          <form @submit.prevent="changePassword" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Текущий пароль</label>
              <input
                v-model="passwordForm.current_password"
                type="password"
                required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Введите текущий пароль"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Новый пароль</label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                required
                minlength="6"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Минимум 6 символов"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Подтвердите новый пароль</label>
              <input
                v-model="passwordForm.new_password2"
                type="password"
                required
                minlength="6"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                placeholder="Повторите новый пароль"
              />
            </div>

            <button
              type="submit"
              :disabled="loadingPassword"
              class="w-full py-3 px-4 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50"
            >
              {{ loadingPassword ? 'Изменение...' : 'Изменить пароль' }}
            </button>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const router = useRouter()
const config = useRuntimeConfig()

const user = ref(null)
const form = ref({
  username: '',
  email: '',
  phone: '',
  beneficiary_category: '',
  region: '',
  snils: ''
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  new_password2: ''
})

const loading = ref(false)
const loadingPassword = ref(false)
const error = ref('')
const success = ref('')

onMounted(async () => {
  // Check if user is logged in
  const token = localStorage.getItem('access_token')
  if (!token) {
    router.push('/login')
    return
  }

  // Get user data
  try {
    user.value = await $fetch(`${config.public.apiBase}/auth/me/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    // Populate form
    form.value = {
      username: user.value.username || '',
      email: user.value.email || '',
      phone: user.value.phone || '',
      beneficiary_category: user.value.beneficiary_category || '',
      region: user.value.region || '',
      snils: user.value.snils || ''
    }
  } catch (err) {
    console.error('Error loading user:', err)
    router.push('/login')
  }
})

const updateProfile = async () => {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const token = localStorage.getItem('access_token')
    const response = await $fetch(`${config.public.apiBase}/auth/me/`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: form.value
    })

    user.value = response
    localStorage.setItem('user', JSON.stringify(response))
    success.value = 'Профиль успешно обновлен'
  } catch (err) {
    error.value = err.data?.message || 'Ошибка при обновлении профиля'
  } finally {
    loading.value = false
  }
}

const changePassword = async () => {
  error.value = ''
  success.value = ''

  if (passwordForm.value.new_password !== passwordForm.value.new_password2) {
    error.value = 'Новые пароли не совпадают'
    return
  }

  loadingPassword.value = true

  try {
    const token = localStorage.getItem('access_token')
    await $fetch(`${config.public.apiBase}/auth/change-password/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: {
        current_password: passwordForm.value.current_password,
        new_password: passwordForm.value.new_password
      }
    })

    success.value = 'Пароль успешно изменен'
    passwordForm.value = {
      current_password: '',
      new_password: '',
      new_password2: ''
    }
  } catch (err) {
    error.value = err.data?.message || 'Ошибка при изменении пароля. Проверьте текущий пароль.'
  } finally {
    loadingPassword.value = false
  }
}

useHead({
  title: 'Профиль | Опора',
  meta: [
    { name: 'description', content: 'Управление профилем пользователя' }
  ]
})
</script>
