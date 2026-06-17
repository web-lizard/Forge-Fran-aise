<script setup lang="ts">
import { onMounted, ref } from 'vue'
import VoiceSelector from '../components/audio/VoiceSelector.vue'
import RankBadge from '../components/imperial/RankBadge.vue'
import { apiGet } from '../lib/api'
import { useAudioStore } from '../stores/audioStore'
import { useBootstrapStore } from '../stores/bootstrapStore'
import { useSettingsStore } from '../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()
const audio = useAudioStore()
const summary = ref<any | null>(null)

onMounted(async () => {
  await bootstrap.load()
  settings.hydrateFromBootstrap()
  summary.value = await apiGet('/progress/local_lizard/summary')
  await audio.loadCache()
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Profil</div>
      <h1>{{ bootstrap.payload?.profile?.display_name ?? 'Local Lizard' }}</h1>
    </div>

    <RankBadge
      :rank-id="bootstrap.payload?.profile?.rank_id"
      :score="summary?.score ?? 0"
    />

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

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
      <VoiceSelector />
    </div>

    <div class="study-card">
      <h2>Audio cache</h2>
      <div class="stat-grid" v-if="audio.cache">
        <div>
          <strong>{{ audio.cache.count }}</strong>
          <span>files</span>
        </div>
        <div>
          <strong>{{ audio.cache.total_mb }}</strong>
          <span>mb</span>
        </div>
        <div>
          <strong>{{ audio.cache.indexed_count }}</strong>
          <span>indexed</span>
        </div>
      </div>
      <button class="ghost-button wide" type="button" @click="audio.clearCache">
        Очистить аудио-кэш
      </button>
    </div>

    <div class="study-card" v-if="summary?.weak_topics?.length">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Слабые темы' : 'Points faibles' }}</h2>
      <div class="chip-row">
        <span v-for="tag in summary.weak_topics" :key="tag" class="stat-chip">{{ tag }}</span>
      </div>
    </div>

    <RouterLink class="primary-button" to="/diagnostics">
      {{ settings.uiLanguage === 'ru' ? 'Открыть диагностику' : 'Ouvrir le diagnostic' }}
    </RouterLink>
  </section>
</template>
