<template>
  <div>
    <NuxtPage />
  </div>
</template>

<script setup>
const { applySettings } = useAccessibility()
const { setupGlobalListener } = useTextToSpeech()

// Apply accessibility settings on mount
onMounted(() => {
  applySettings()
  
  // Setup global text-to-speech listener for Ctrl+Enter
  const cleanup = setupGlobalListener()
  
  // Cleanup on unmount
  onUnmounted(() => {
    if (cleanup) cleanup()
  })
})
</script>
