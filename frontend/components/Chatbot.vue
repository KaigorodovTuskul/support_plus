<template>
  <!-- Floating Mode (for non-dashboard pages) -->
  <div v-if="!inline" class="fixed bottom-4 right-4 z-50">
    <!-- Chat Toggle Button -->
    <button
      v-if="!isOpen"
      @click="toggleChat"
      class="bg-primary-600 hover:bg-primary-700 text-white rounded-full p-4 shadow-lg transition"
      aria-label="Открыть чат"
    >
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
      </svg>
    </button>

    <!-- Chat Window (Floating) -->
    <div
      v-else
      class="bg-white rounded-lg shadow-2xl w-96 h-[600px] flex flex-col"
    >
      <!-- Header -->
      <div class="bg-primary-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <h3 class="font-semibold">Чат-бот помощник</h3>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="clearHistory"
            class="p-1 hover:bg-primary-700 rounded transition"
            title="Очистить историю"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
          <button
            @click="toggleChat"
            class="p-1 hover:bg-primary-700 rounded transition"
            aria-label="Закрыть чат"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Messages -->
      <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4">
        <div v-if="messages.length === 0" class="text-center text-gray-500 mt-8">
          <p>Привет! Я помогу вам найти информацию о льготах.</p>
          <p class="text-sm mt-2">Задайте мне любой вопрос!</p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="flex"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[80%] rounded-lg p-3"
            :class="msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'"
          >
            <div class="flex flex-col space-y-2">
              <p class="text-sm whitespace-pre-wrap">{{ getMessageText(msg.content) }}</p>
              <button 
                v-if="getSearchQuery(msg.content)"
                @click="navigateToBenefits(getSearchQuery(msg.content))"
                class="self-start text-xs bg-white text-primary-600 border border-primary-200 px-3 py-1.5 rounded-full hover:bg-primary-50 transition flex items-center space-x-1 shadow-sm mt-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Посмотреть льготы</span>
              </button>
            </div>
            <div class="flex items-center justify-between mt-1">
              <p class="text-xs opacity-75">
                {{ formatTime(msg.timestamp) }}
              </p>
              <!-- Play/Stop button for assistant messages -->
              <button
                v-if="msg.role === 'assistant'"
                @click="togglePlayMessage(msg, index)"
                class="ml-2 p-1 rounded hover:bg-gray-200 transition"
                :class="{'text-green-600': playingMessageIndex === index}"
                :title="playingMessageIndex === index ? 'Остановить' : 'Воспроизвести'"
              >
                <svg v-if="playingMessageIndex !== index" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-gray-100 rounded-lg p-3">
            <div class="flex space-x-2">
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Voice Controls -->
      <div v-if="isRecording || isPlaying" class="px-4 py-2 bg-gray-50 border-t">
        <div v-if="isRecording" class="flex items-center space-x-2 text-red-600">
          <div class="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
          <span class="text-sm">Идет запись...</span>
          <button @click="stopRecording" class="ml-auto text-xs bg-red-600 text-white px-3 py-1 rounded">
            Остановить
          </button>
        </div>
        <div v-if="isPlaying" class="flex items-center space-x-2 text-green-600">
          <svg class="w-4 h-4 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4l15 8-15 8V4z"/>
          </svg>
          <span class="text-sm">Воспроизведение...</span>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-4 border-t">
        <div class="flex space-x-2">
          <button
            @click="toggleRecording"
            :disabled="isLoading"
            class="p-2 rounded-lg transition"
            :class="isRecording ? 'bg-red-100 text-red-600 hover:bg-red-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            title="Голосовой ввод"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
          <input
            v-model="currentMessage"
            @keypress.enter="sendMessage"
            type="text"
            placeholder="Введите сообщение..."
            class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
            :disabled="isLoading || isRecording"
          />
          <button
            @click="sendMessage"
            :disabled="!currentMessage.trim() || isLoading || isRecording"
            class="bg-primary-600 text-white p-2 rounded-lg hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Inline Mode (for dashboard) -->
  <div v-else class="w-full">
    <!-- Inline Chat Header with Robot -->
    <div class="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-6 rounded-t-lg">
      <div class="flex items-center space-x-4">
        <!-- Dancing Robot Gif -->
        <img
          src="/roboto_128.gif"
          alt="Робот-помощник"
          class="w-16 h-16 object-contain"
        />
        <div class="flex-1">
          <h2 class="text-2xl font-bold">Чат-бот помощник</h2>
          <p class="text-sm opacity-90">Задайте вопрос о льготах и выплатах</p>
        </div>
        <button
          @click="clearHistory"
          class="p-2 hover:bg-primary-800 rounded transition"
          title="Очистить историю"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Inline Chat Body -->
    <div class="bg-white shadow-lg rounded-b-lg">
      <!-- Messages -->
      <div ref="messagesContainer" class="h-96 overflow-y-auto p-6 space-y-4 bg-gray-50">
        <div v-if="messages.length === 0" class="text-center text-gray-500 mt-8">
          <p class="text-lg">Привет! Я помогу вам найти информацию о льготах.</p>
          <p class="text-sm mt-2">Задайте мне любой вопрос!</p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="flex"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div
            class="max-w-[70%] rounded-lg p-4 shadow-sm"
            :class="msg.role === 'user' ? 'bg-primary-600 text-white' : 'bg-white border border-gray-200 text-gray-900'"
          >
            <div class="flex flex-col space-y-2">
              <p class="text-sm whitespace-pre-wrap">{{ getMessageText(msg.content) }}</p>
              <button 
                v-if="getSearchQuery(msg.content)"
                @click="navigateToBenefits(getSearchQuery(msg.content))"
                class="self-start text-xs bg-primary-50 text-primary-700 border border-primary-200 px-3 py-1.5 rounded-full hover:bg-primary-100 transition flex items-center space-x-1 shadow-sm mt-2"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span>Посмотреть льготы</span>
              </button>
            </div>
            <div class="flex items-center justify-between mt-1">
              <p class="text-xs opacity-75">
                {{ formatTime(msg.timestamp) }}
              </p>
              <!-- Play/Stop button for assistant messages -->
              <button
                v-if="msg.role === 'assistant'"
                @click="togglePlayMessage(msg, index)"
                class="ml-2 p-1 rounded hover:bg-gray-200 transition"
                :class="{'text-green-600': playingMessageIndex === index}"
                :title="playingMessageIndex === index ? 'Остановить' : 'Воспроизвести'"
              >
                <svg v-if="playingMessageIndex !== index" class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z"/>
                </svg>
                <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="flex justify-start">
          <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div class="flex space-x-2">
              <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style="animation-delay: 0s"></div>
              <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
              <div class="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Voice Controls -->
      <div v-if="isRecording || isPlaying" class="px-6 py-3 bg-gray-50 border-t">
        <div v-if="isRecording" class="flex items-center space-x-2 text-red-600">
          <div class="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
          <span class="text-sm font-medium">Идет запись...</span>
          <button @click="stopRecording" class="ml-auto text-xs bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition">
            Остановить
          </button>
        </div>
        <div v-if="isPlaying" class="flex items-center space-x-2 text-green-600">
          <svg class="w-4 h-4 animate-pulse" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6 4l15 8-15 8V4z"/>
          </svg>
          <span class="text-sm font-medium">Воспроизведение...</span>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-6 border-t">
        <div class="flex space-x-3">
          <button
            @click="toggleRecording"
            :disabled="isLoading"
            class="p-3 rounded-lg transition shadow-sm"
            :class="isRecording ? 'bg-red-100 text-red-600 hover:bg-red-200' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
            title="Голосовой ввод"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </button>
          <input
            v-model="currentMessage"
            @keypress.enter="sendMessage"
            type="text"
            placeholder="Введите сообщение..."
            class="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 shadow-sm"
            :disabled="isLoading || isRecording"
          />
          <button
            @click="sendMessage"
            :disabled="!currentMessage.trim() || isLoading || isRecording"
            class="bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Define props for inline/floating mode
const props = defineProps({
  inline: {
    type: Boolean,
    default: false
  }
})


const config = useRuntimeConfig()
const { settings } = useAccessibility()
const isOpen = ref(false)
const messages = ref([])
const currentMessage = ref('')
const isLoading = ref(false)
const isRecording = ref(false)
const isPlaying = ref(false)
const messagesContainer = ref(null)
const playingMessageIndex = ref(null)

let mediaRecorder = null
let audioChunks = []
let currentUtterance = null

const toggleChat = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loadHistory()
  }
}

// Auto-open and load history in inline mode
onMounted(() => {
  if (props.inline) {
    isOpen.value = true
    loadHistory()
  }
})

const loadHistory = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    const data = await $fetch(`${config.public.apiBase}/chat/history/`, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    messages.value = data.history.flatMap(msg => [
      {
        role: 'user',
        content: msg.message,
        timestamp: msg.timestamp
      },
      {
        role: 'assistant',
        content: msg.response,
        timestamp: msg.timestamp
      }
    ])

    nextTick(() => scrollToBottom())
  } catch (err) {
    console.error('Error loading chat history:', err)
  }
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return

  const token = localStorage.getItem('access_token')
  if (!token) return

  const userMessage = currentMessage.value
  currentMessage.value = ''

  // Add user message to UI
  messages.value.push({
    role: 'user',
    content: userMessage,
    timestamp: new Date()
  })

  nextTick(() => scrollToBottom())

  isLoading.value = true

  try {
    const data = await $fetch(`${config.public.apiBase}/chat/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: {
        message: userMessage
      }
    })

    // Add assistant response
    messages.value.push({
      role: 'assistant',
      content: data.response,
      timestamp: data.timestamp
    })

    nextTick(() => scrollToBottom())

    // Handle search redirect - REMOVED (now using button in message)
    // if (data.search_query) { ... }

    // Don't auto-play - user will click play button if needed
  } catch (err) {
    console.error('Error sending message:', err)
    messages.value.push({
      role: 'assistant',
      content: 'Извините, произошла ошибка. Попробуйте еще раз.',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
  }
}

const toggleRecording = async () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    // Use Web Speech API for speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition

    if (!SpeechRecognition) {
      alert('Ваш браузер не поддерживает распознавание речи. Попробуйте использовать Chrome или Edge.')
      return
    }

    const recognition = new SpeechRecognition()
    recognition.lang = 'ru-RU'
    recognition.continuous = false
    recognition.interimResults = false

    recognition.onstart = () => {
      isRecording.value = true
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript
      currentMessage.value = transcript
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      isRecording.value = false
      if (event.error === 'no-speech') {
        alert('Речь не распознана. Попробуйте еще раз.')
      } else if (event.error === 'not-allowed') {
        alert('Доступ к микрофону запрещен. Разрешите доступ в настройках браузера.')
      }
    }

    recognition.onend = () => {
      isRecording.value = false
    }

    recognition.start()
    mediaRecorder = recognition // Store for stopping later
  } catch (err) {
    console.error('Error starting recording:', err)
    alert('Не удалось получить доступ к микрофону')
  }
}

const stopRecording = () => {
  if (mediaRecorder && isRecording.value) {
    mediaRecorder.stop()
    isRecording.value = false
  }
}

const transcribeAudio = async (audioBlob) => {
  // Use Web Speech API for speech recognition
  // The audioBlob is not needed as we'll use SpeechRecognition directly
  // This function is kept for compatibility but does nothing
  // The actual recognition is handled in startRecording()
}

const playTextAsSpeech = async (text, messageIndex = null) => {
  try {
    // Use Web Speech API for text-to-speech
    if (!('speechSynthesis' in window)) {
      console.warn('Text-to-speech not supported in this browser')
      return
    }

    isPlaying.value = true
    if (messageIndex !== null) {
      playingMessageIndex.value = messageIndex
    }

    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'ru-RU'
    utterance.rate = settings.value.speechRate || 1.5
    utterance.pitch = 1.0

    utterance.onend = () => {
      isPlaying.value = false
      playingMessageIndex.value = null
      currentUtterance = null
    }

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event.error)
      isPlaying.value = false
      playingMessageIndex.value = null
      currentUtterance = null
    }

    currentUtterance = utterance
    window.speechSynthesis.speak(utterance)
  } catch (err) {
    console.error('Error playing audio:', err)
    isPlaying.value = false
    playingMessageIndex.value = null
  }
}

const stopTextAsSpeech = () => {
  if (window.speechSynthesis && window.speechSynthesis.speaking) {
    window.speechSynthesis.cancel()
    isPlaying.value = false
    playingMessageIndex.value = null
    currentUtterance = null
  }
}

const togglePlayMessage = (message, index) => {
  if (playingMessageIndex.value === index) {
    // Stop playing
    stopTextAsSpeech()
  } else {
    // Stop any current playback and play new message
    stopTextAsSpeech()
    playTextAsSpeech(message.content, index)
  }
}

const clearHistory = async () => {
  if (!confirm('Вы уверены, что хотите очистить историю чата?')) return

  const token = localStorage.getItem('access_token')
  if (!token) return

  try {
    await $fetch(`${config.public.apiBase}/chat/clear/`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })

    messages.value = []
  } catch (err) {
    console.error('Error clearing history:', err)
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

// Message parsing helpers
const getSearchQuery = (content) => {
  if (!content) return null
  const match = content.match(/\[SEARCH: (.*?)\]/)
  return match ? match[1] : null
}

const getMessageText = (content) => {
  if (!content) return ''
  return content.replace(/\[SEARCH: .*?\]/, '').trim()
}

const navigateToBenefits = (query) => {
  navigateTo({
    path: '/benefits',
    query: { search: query }
  })
  if (!props.inline) {
    isOpen.value = false
  }
}
</script>
