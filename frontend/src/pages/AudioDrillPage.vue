<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import VoiceSelector from '../components/audio/VoiceSelector.vue'
import AudioButton from '../components/learning/AudioButton.vue'
import { apiGet } from '../lib/api'
import { useAudioStore } from '../stores/audioStore'
import { useBootstrapStore } from '../stores/bootstrapStore'
import { useSettingsStore } from '../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()
const audio = useAudioStore()

const session = ref<any | null>(null)
const index = ref(0)
const showTranslation = ref(false)

const current = computed(() => session.value?.exercises?.[index.value] ?? null)
const total = computed(() => session.value?.exercises?.length ?? 0)

async function load() {
  await bootstrap.load()
  settings.hydrateFromBootstrap()
  session.value = await apiGet('/review/local_lizard/session?mode=audio&limit=10')
  index.value = 0
  showTranslation.value = false
  await audio.loadCache()
}

function next() {
  if (index.value < total.value - 1) {
    index.value += 1
    showTranslation.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="page">
    <div class="section-title compact-title">
      <div class="eyebrow">Audio Drill</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Аудио-дрель' : 'Drill audio' }}</h1>
      <p>
        {{
          settings.uiLanguage === 'ru'
            ? 'Слушаем французский, повторяем, потом раскрываем перевод.'
            : 'Écoute, répète, puis ouvre la traduction.'
        }}
      </p>
    </div>

    <div class="study-card">
      <h2>{{ settings.uiLanguage === 'ru' ? 'Голос' : 'Voix' }}</h2>
      <VoiceSelector />
    </div>

    <template v-if="current">
      <div class="practice-head">
        <span>{{ index + 1 }} / {{ total }}</span>
        <span>{{ current.section_id }}</span>
      </div>

      <div class="lesson-progress">
        <div :style="{ width: ((index + 1) / total * 100) + '%' }"></div>
      </div>

      <article class="study-card audio-drill-card">
        <div class="crest-orb">♪</div>
        <div class="eyebrow">Écoute</div>

        <h2>{{ current.audio_text }}</h2>

        <div class="audio-grid">
          <AudioButton :text="current.audio_text" label="Normal" />
          <AudioButton :text="current.audio_text" label="Lentement" mode="slow" />
        </div>

        <button class="ghost-button wide" type="button" @click="showTranslation = !showTranslation">
          {{ showTranslation ? 'Скрыть перевод' : 'Показать перевод' }}
        </button>

        <div v-if="showTranslation" class="result-box good">
          <strong>{{ current.prompt?.ru }}</strong>
          <p>{{ current.explanation?.ru }}</p>
        </div>

        <button class="primary-button" type="button" @click="next">
          {{ settings.uiLanguage === 'ru' ? 'Следующее' : 'Suivant' }}
        </button>
      </article>
    </template>

    <div v-if="audio.cache" class="study-card">
      <h2>Audio cache</h2>
      <div class="stat-grid">
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
        Очистить кэш
      </button>
    </div>
  </section>
</template>
