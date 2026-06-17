<script setup lang="ts">
import { onMounted } from 'vue'
import ExerciseRenderer from '../components/practice/ExerciseRenderer.vue'
import { usePracticeStore, type PracticeMode } from '../stores/practiceStore'
import { useSettingsStore } from '../stores/settingsStore'

const practice = usePracticeStore()
const settings = useSettingsStore()

const modes: { id: PracticeMode; ru: string; fr: string }[] = [
  { id: 'quick', ru: 'Быстро', fr: 'Rapide' },
  { id: 'weak', ru: 'Слабое', fr: 'Faible' },
  { id: 'audio', ru: 'Аудио', fr: 'Audio' },
  { id: 'articles', ru: 'Артикли', fr: 'Articles' },
  { id: 'vulgar', ru: 'Мат', fr: 'Gros mots' },
]

onMounted(() => {
  practice.load('quick')
})

function modeLabel(mode: { ru: string; fr: string }) {
  return settings.uiLanguage === 'ru' ? mode.ru : mode.fr
}

function onAnswered(payload: any) {
  practice.markAnswered(payload)
}
</script>

<template>
  <section class="page">
    <div class="section-title compact-title">
      <div class="eyebrow">Drill</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Тренировка' : 'Entraînement' }}</h1>
      <p>
        {{
          settings.uiLanguage === 'ru'
            ? 'Короткая сессия на один экран. Без перегруза, только удар по слабым местам.'
            : 'Session courte, mobile-first, sans surcharge.'
        }}
      </p>
    </div>

    <div class="chip-row">
      <button
        v-for="mode in modes"
        :key="mode.id"
        class="ghost-button"
        :class="{ active: practice.mode === mode.id }"
        type="button"
        @click="practice.load(mode.id)"
      >
        {{ modeLabel(mode) }}
      </button>
    </div>

    <div v-if="practice.loading" class="soft-card">Загрузка...</div>
    <div v-else-if="practice.error" class="soft-card">{{ practice.error }}</div>

    <template v-else-if="practice.currentExercise">
      <div class="practice-head">
        <span>{{ practice.currentIndex + 1 }} / {{ practice.total }}</span>
        <span>{{ practice.correct }} correct</span>
        <span>{{ practice.accuracy }}%</span>
      </div>

      <div class="lesson-progress">
        <div :style="{ width: ((practice.currentIndex + 1) / practice.total * 100) + '%' }"></div>
      </div>

      <div class="study-card">
        <ExerciseRenderer
          :lesson-id="practice.currentExercise.lesson_id"
          :exercise="practice.currentExercise"
          @answered="onAnswered"
        />

        <button class="primary-button" type="button" @click="practice.next">
          {{ settings.uiLanguage === 'ru' ? 'Следующий удар' : 'Coup suivant' }}
        </button>
      </div>
    </template>

    <div v-else class="hero-card">
      <div class="crest-orb">✓</div>
      <div class="eyebrow">Session complete</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Дрель завершена' : 'Session terminée' }}</h1>
      <p>
        {{ practice.correct }} / {{ practice.answered }}
        correct, {{ practice.accuracy }}%
      </p>
      <button class="primary-button" type="button" @click="practice.load(practice.mode)">
        {{ settings.uiLanguage === 'ru' ? 'Повторить' : 'Recommencer' }}
      </button>
    </div>
  </section>
</template>
