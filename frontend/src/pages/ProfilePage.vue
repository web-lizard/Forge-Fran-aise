<script setup lang="ts">
import { onMounted, ref } from 'vue'
import VoiceSelector from '../components/audio/VoiceSelector.vue'
import { apiGet } from '../lib/api'
import { useBootstrapStore } from '../stores/bootstrapStore'
import { useSettingsStore } from '../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()
const summary = ref<any | null>(null)

onMounted(async () => {
  await bootstrap.load()
  settings.hydrateFromBootstrap()
  summary.value = await apiGet('/progress/local_lizard/summary')
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
      <h2>{{ settings.uiLanguage === 'ru' ? 'Прогресс' : 'Progression' }}</h2>
      <div class="stat-grid" v-if="summary">
        <div>
          <strong>{{ summary.score }}</strong>
          <span>score</span>
        </div>
        <div>
          <strong>{{ summary.accuracy }}%</strong>
          <span>accuracy</span>
        </div>
        <div>
          <strong>{{ summary.completed_count }}</strong>
          <span>lessons</span>
        </div>
      </div>
    </div>

    <div class="study-card" v-if="summary?.weak_topics?.length">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Слабые темы' : 'Points faibles' }}</h2>
      <div class="chip-row">
        <span v-for="tag in summary.weak_topics" :key="tag" class="stat-chip">{{ tag }}</span>
      </div>
    </div>

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Текущий ранг' : 'Grade actuel' }}</h2>
      <p>{{ bootstrap.payload?.profile?.rank_id }}</p>
    </div>

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
      <VoiceSelector />
    </div>
  </section>
</template>
