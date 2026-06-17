<script setup lang="ts">
import { ref } from 'vue'
import { apiPost, publicApiUrl } from '../../lib/api'
import { useSettingsStore } from '../../stores/settingsStore'

const props = defineProps<{
  text: string
  label?: string
  mode?: string
  compact?: boolean
}>()

const settings = useSettingsStore()
const loading = ref(false)
const status = ref('')

function browserFallbackSpeak() {
  if (!('speechSynthesis' in window)) {
    status.value = 'no speech'
    return
  }

  window.speechSynthesis.cancel()

  const utterance = new SpeechSynthesisUtterance(props.text)
  utterance.lang = 'fr-FR'
  utterance.rate = props.mode === 'slow' ? 0.75 : 0.95
  utterance.pitch = 1

  status.value = 'browser'
  window.speechSynthesis.speak(utterance)
}

async function play() {
  loading.value = true
  status.value = '...'

  try {
    const result = await apiPost<{
      url: string
      fallback?: boolean
      provider?: string
      format?: string
    }>('/audio/speak', {
      text: props.text,
      lang: 'fr',
      voice_id: settings.voiceId || 'edge_fr_denise',
      speed: props.mode === 'slow' ? 0.75 : 1,
      mode: props.mode ?? 'normal',
    })

    if (result.fallback || result.provider === 'mock') {
      browserFallbackSpeak()
      return
    }

    const audio = new Audio(publicApiUrl(result.url))

    audio.onplaying = () => {
      status.value = 'playing'
    }

    audio.onended = () => {
      status.value = ''
    }

    audio.onerror = () => {
      browserFallbackSpeak()
    }

    await audio.play()
  } catch (error) {
    console.error('AudioButton error:', error)
    browserFallbackSpeak()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <button
    class="audio-button"
    :class="{ compact }"
    type="button"
    :disabled="loading"
    @click="play"
  >
    <span v-if="loading">...</span>
    <span v-else>▶</span>
    {{ status || label || 'Слушать' }}
  </button>
</template>
