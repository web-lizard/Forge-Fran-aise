<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AudioButton from '../components/learning/AudioButton.vue'
import { apiGet } from '../lib/api'
import { useSettingsStore } from '../stores/settingsStore'

const settings = useSettingsStore()
const items = ref<any[]>([])
const activeTag = ref('all')

const filteredItems = computed(() => {
  if (activeTag.value === 'all') return items.value
  return items.value.filter((item) => item.tags?.includes(activeTag.value) || item.pack_id === activeTag.value)
})

onMounted(async () => {
  items.value = await apiGet<any[]>('/vulgar/items')
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Adult Codex</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Французский мат' : 'Gros mots français' }}</h1>
      <p>
        {{
          settings.uiLanguage === 'ru'
            ? 'Грубые фразы с уровнем опасности, переводом и озвучкой.'
            : 'Phrases vulgaires avec niveau de danger et audio.'
        }}
      </p>
    </div>

    <div class="chip-row">
      <button class="ghost-button" type="button" @click="activeTag = 'all'">all</button>
      <button class="ghost-button" type="button" @click="activeTag = 'anger_basic'">anger</button>
      <button class="ghost-button" type="button" @click="activeTag = 'go_away'">go away</button>
      <button class="ghost-button" type="button" @click="activeTag = 'office_rage'">office</button>
    </div>

    <article v-for="item in filteredItems" :key="item.id" class="study-card danger-card">
      <div class="rudeness">Грубость {{ item.rudeness_level }}/5</div>
      <h2>{{ item.fr }}</h2>
      <p class="transcription">{{ item.transcription }}</p>
      <p>{{ item.ru }}</p>
      <AudioButton :text="item.audio_text" label="Слушать" />

      <details class="mini-details">
        <summary>Контекст и мягкий вариант</summary>
        <p>{{ item.context.ru }}</p>
        <p v-if="item.softer_versions?.[0]">
          Мягче: <strong>{{ item.softer_versions[0].fr }}</strong>
          {{ item.softer_versions[0].ru }}
        </p>
      </details>
    </article>
  </section>
</template>
