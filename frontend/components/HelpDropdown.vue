<template>
  <div class="relative" @mouseenter="isOpen = true" @mouseleave="isOpen = false">
    <button
      class="px-4 py-2 text-gray-700 hover:text-primary-600 font-semibold transition focus:outline-none focus:ring-2 focus:ring-primary-500 rounded"
    >
      Как помочь
    </button>

    <!-- Dropdown Menu -->
    <transition
      enter-active-class="transition ease-out duration-100"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-show="isOpen"
        class="absolute left-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50"
      >
        <div class="py-1">
          <NuxtLink
            to="/donate/individual"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition"
            @click="isOpen = false"
          >
            Частным лицам
          </NuxtLink>
          <NuxtLink
            to="/donate/corporate"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition"
            @click="isOpen = false"
          >
            Компаниям
          </NuxtLink>
          <NuxtLink
            to="/donate/leaderboard"
            class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition"
            @click="isOpen = false"
          >
            Нам помогают
          </NuxtLink>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
const isOpen = ref(false)
</script>
