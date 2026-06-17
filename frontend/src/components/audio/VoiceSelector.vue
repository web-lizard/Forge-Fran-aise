<script setup lang="ts">
import { computed } from 'vue'
import { useBootstrapStore } from '../../stores/bootstrapStore'
import { useSettingsStore } from '../../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()

const voices = computed(() => bootstrap.payload?.voices ?? [])
</script>

<template>
  <div class="voice-selector">
    <label for="voice">Голос</label>
    <select id="voice" :value="settings.voiceId" @change="settings.setVoice(($event.target as HTMLSelectElement).value)">
      <option v-for="voice in voices" :key="voice.id" :value="voice.id">
        {{ voice.label }}
      </option>
    </select>
  </div>
</template>
