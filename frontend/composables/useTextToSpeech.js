export const useTextToSpeech = () => {
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel()

      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'ru-RU'
      utterance.rate = 1.0
      utterance.pitch = 1.0

      window.speechSynthesis.speak(utterance)
    } else {
      console.error('Speech synthesis not supported')
    }
  }

  const stop = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel()
    }
  }

  const setupGlobalListener = () => {
    if (process.client) {
      const handleKeyDown = (event) => {
        if (event.ctrlKey && event.key === 'Enter') {
          event.preventDefault()
          const selection = window.getSelection().toString().trim()
          if (selection) {
            speak(selection)
          }
        }
      }

      document.addEventListener('keydown', handleKeyDown)

      // Return cleanup function
      return () => {
        document.removeEventListener('keydown', handleKeyDown)
      }
    }
  }

  return { speak, stop, setupGlobalListener }
}
