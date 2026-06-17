<script setup lang="ts">
import { ref } from 'vue'
import { apiPost, publicApiUrl } from '../../lib/api'
import { useSettingsStore } from '../../stores/settingsStore'

const props = defineProps<{
  text: string
  label?: string
  mode?: string
}>()

const settings = useSettingsStore()
const loading = ref(false)

async function play() {
  loading.value = true

  try {
    const result = await apiPost<{ url: string }>('/audio/speak', {
      text: props.text,
      lang: 'fr',
      voice_id: settings.voiceId,
      speed: props.mode === 'slow' ? 0.75 : 1,
      mode: props.mode ?? 'normal',
    })

    const audio = new Audio(publicApiUrl(result.url))
    await audio.play()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <button class="audio-button" type="button" :disabled="loading" @click="play">
    <span v-if="loading">...</span>
    <span v-else>▶</span>
    {{ label ?? 'Слушать' }}
  </button>
</template>
