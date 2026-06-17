<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import CardRenderer from '../components/learning/CardRenderer.vue'
import { apiGet } from '../lib/api'
import { t } from '../lib/i18n'
import { useSettingsStore } from '../stores/settingsStore'

const route = useRoute()
const settings = useSettingsStore()
const lesson = ref<any | null>(null)
const loading = ref(false)
const cardIndex = ref(0)

const currentCard = computed(() => lesson.value?.cards?.[cardIndex.value] ?? null)
const totalCards = computed(() => lesson.value?.cards?.length ?? 0)

async function loadLesson() {
  loading.value = true
  cardIndex.value = 0
  lesson.value = await apiGet<any>('/lessons/' + route.params.lessonId)
  loading.value = false
}

function nextCard() {
  if (cardIndex.value < totalCards.value - 1) {
    cardIndex.value += 1
  }
}

function prevCard() {
  if (cardIndex.value > 0) {
    cardIndex.value -= 1
  }
}

onMounted(loadLesson)
watch(() => route.params.lessonId, loadLesson)
</script>

<template>
  <section class="page lesson-page">
    <div v-if="loading" class="soft-card">Загрузка...</div>

    <template v-if="lesson && currentCard">
      <div class="section-title compact-title">
        <div class="eyebrow">{{ lesson.level }} / {{ cardIndex + 1 }} из {{ totalCards }}</div>
        <h1>{{ t(lesson.title, settings.uiLanguage) }}</h1>
      </div>

      <div class="lesson-progress">
        <div :style="{ width: ((cardIndex + 1) / totalCards * 100) + '%' }"></div>
      </div>

      <CardRenderer :lesson="lesson" :card="currentCard" />

      <div class="lesson-nav-row">
        <button class="ghost-button" type="button" :disabled="cardIndex === 0" @click="prevCard">
          ←
        </button>
        <RouterLink class="ghost-button" to="/campaign">
          {{ settings.uiLanguage === 'ru' ? 'Карта' : 'Carte' }}
        </RouterLink>
        <button class="primary-button" type="button" :disabled="cardIndex >= totalCards - 1" @click="nextCard">
          {{ settings.uiLanguage === 'ru' ? 'Дальше' : 'Suivant' }}
        </button>
      </div>
    </template>
  </section>
</template>
