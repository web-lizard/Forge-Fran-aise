<script setup lang="ts">
import { computed } from 'vue'
import { useBootstrapStore } from '../../stores/bootstrapStore'
import { useSettingsStore } from '../../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()

const voices = computed(() => bootstrap.payload?.voices ?? [])
const edgeVoices = computed(() => voices.value.filter((voice) => voice.engine === 'edge'))
const mockVoices = computed(() => voices.value.filter((voice) => voice.engine === 'mock'))
</script>

<template>
  <div class="voice-selector">
    <label for="voice">Голос</label>
    <select id="voice" :value="settings.voiceId" @change="settings.setVoice(($event.target as HTMLSelectElement).value)">
      <optgroup label="Edge neural online">
        <option v-for="voice in edgeVoices" :key="voice.id" :value="voice.id">
          {{ voice.label }}
        </option>
      </optgroup>
      <optgroup label="Mock fallback">
        <option v-for="voice in mockVoices" :key="voice.id" :value="voice.id">
          {{ voice.label }}
        </option>
      </optgroup>
    </select>

    <p class="voice-note">
      Edge-голоса звучат лучше, но требуют интернет. Mock нужен как аварийный fallback.
    </p>
  </div>
</template>
