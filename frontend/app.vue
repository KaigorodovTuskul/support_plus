<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup>
const { applySettings } = useAccessibility()

// Apply accessibility settings on mount
onMounted(() => {
  applySettings()
})
</script>
