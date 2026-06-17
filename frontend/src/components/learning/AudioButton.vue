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
const fallback = ref(false)

async function play() {
  loading.value = true
  fallback.value = false

  try {
    const result = await apiPost<{ url: string; fallback?: boolean }>('/audio/speak', {
      text: props.text,
      lang: 'fr',
      voice_id: settings.voiceId,
      speed: props.mode === 'slow' ? 0.75 : 1,
      mode: props.mode ?? 'normal',
    })

    fallback.value = Boolean(result.fallback)
    const audio = new Audio(publicApiUrl(result.url))
    await audio.play()
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
    {{ label ?? 'Слушать' }}
    <small v-if="fallback">mock</small>
  </button>
</template>
