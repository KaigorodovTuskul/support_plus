export const useAccessibility = () => {
  const settings = useState('accessibilitySettings', () => ({
    fontSize: 'normal',
    fontFamily: 'sans-serif',
    letterSpacing: 'normal',
    colorMode: 'default',
    showImages: true,
    speechAssistant: false,
    theme: 'light', // light or dark
    speechRate: 1.5 // Speech synthesis rate (0.5 - 2.0)
  }))

  // Load settings from localStorage on client side
  if (process.client) {
    const savedSettings = localStorage.getItem('accessibility_settings')
    if (savedSettings) {
      settings.value = { ...settings.value, ...JSON.parse(savedSettings) }
    }
  }

  const saveSettings = () => {
    if (process.client) {
      localStorage.setItem('accessibility_settings', JSON.stringify(settings.value))
      applySettings()
    }
  }

  const applySettings = () => {
    if (!process.client) return

    const html = document.documentElement

    // Remove all accessibility classes
    html.classList.remove(
      'font-size-normal', 'font-size-enlarged', 'font-size-huge',
      'font-sans-serif', 'font-serif',
      'letter-spacing-normal', 'letter-spacing-enlarged', 'letter-spacing-huge',
      'color-mode-default', 'color-mode-monochrome', 'color-mode-inverted', 'color-mode-blue-bg',
      'hide-images',
      'dark'
    )

    // Apply font size
    html.classList.add(`font-size-${settings.value.fontSize}`)

    // Apply font family
    html.classList.add(`font-${settings.value.fontFamily}`)

    // Apply letter spacing
    html.classList.add(`letter-spacing-${settings.value.letterSpacing}`)

    // Apply color mode
    html.classList.add(`color-mode-${settings.value.colorMode}`)

    // Apply image visibility
    if (!settings.value.showImages) {
      html.classList.add('hide-images')
    }

    // Apply theme (dark mode)
    if (settings.value.theme === 'dark') {
      html.classList.add('dark')
    }
  }

  const resetSettings = () => {
    settings.value = {
      fontSize: 'normal',
      fontFamily: 'sans-serif',
      letterSpacing: 'normal',
      colorMode: 'default',
      showImages: true,
      speechAssistant: false,
      theme: 'light',
      speechRate: 1.5
    }
    saveSettings()
  }

  const updateSetting = (key, value) => {
    settings.value[key] = value
    saveSettings()
  }

  // Apply settings on mount
  if (process.client) {
    applySettings()
  }

  return {
    settings,
    saveSettings,
    applySettings,
    resetSettings,
    updateSetting
  }
}
