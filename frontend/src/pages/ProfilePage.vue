<script setup lang="ts">
import { onMounted } from 'vue'
import VoiceSelector from '../components/audio/VoiceSelector.vue'
import { useBootstrapStore } from '../stores/bootstrapStore'
import { useSettingsStore } from '../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()

onMounted(async () => {
  await bootstrap.load()
  settings.hydrateFromBootstrap()
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Profil</div>
      <h1>{{ bootstrap.payload?.profile?.display_name ?? 'Local Lizard' }}</h1>
    </div>

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Интерфейс' : 'Interface' }}</h2>
      <button class="primary-button" type="button" @click="settings.toggleLanguage">
        {{ settings.uiLanguage === 'ru' ? 'Переключить на французский' : 'Passer en russe' }}
      </button>
    </div>

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Текущий ранг' : 'Grade actuel' }}</h2>
      <p>{{ bootstrap.payload?.profile?.rank_id }}</p>
    </div>

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
      <VoiceSelector />
    </div>

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Доступные голоса' : 'Voix disponibles' }}</h2>
      <div v-for="voice in bootstrap.payload?.voices ?? []" :key="voice.id" class="codex-row">
        <strong>{{ voice.label }}</strong>
        <span>{{ voice.engine }} / {{ voice.quality }}</span>
      </div>
    </div>
  </section>
</template>
