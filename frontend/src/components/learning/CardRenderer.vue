<script setup lang="ts">
import { t, ui } from '../../lib/i18n'
import { useSettingsStore } from '../../stores/settingsStore'
import AudioButton from './AudioButton.vue'
import ExerciseRenderer from '../practice/ExerciseRenderer.vue'

const props = defineProps<{
  lesson: any
  card: any
}>()

const settings = useSettingsStore()

function exerciseById(exerciseId: string) {
  return props.lesson?.exercises?.find((item: any) => item.id === exerciseId)
}

function explain(card: any) {
  const title = settings.uiLanguage === 'ru' ? 'Пояснение' : 'Explication'
  const body = card.tooltip
    ? t(card.tooltip, settings.uiLanguage)
    : settings.uiLanguage === 'ru'
      ? 'Подробный разбор будет добавлен в Кодекс.'
      : 'Une explication détaillée sera ajoutée au Codex.'

  settings.openSheet(title, body)
}
</script>

<template>
  <article class="study-card">
    <template v-if="card.type === 'theory'">
      <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Теория' : 'Théorie' }}</div>
      <h2>{{ t(card.title, settings.uiLanguage) }}</h2>
      <p>{{ t(card.body, settings.uiLanguage) }}</p>
      <button
        class="ghost-button wide"
        type="button"
        @click="settings.openSheet(t(card.title, settings.uiLanguage), t(card.body, settings.uiLanguage))"
      >
        {{ ui('why', settings.uiLanguage) }}
      </button>
    </template>

    <template v-else-if="card.type === 'word'">
      <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Слово' : 'Mot' }}</div>
      <h2>{{ card.fr }}</h2>
      <p class="transcription">{{ card.transcription }}</p>
      <p>{{ card.ru }}</p>
      <div class="button-row">
        <AudioButton :text="card.audio_text" :label="ui('listen', settings.uiLanguage)" />
        <button class="ghost-button" type="button" @click="explain(card)">
          ?
        </button>
      </div>
    </template>

    <template v-else-if="card.type === 'example'">
      <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Пример' : 'Exemple' }}</div>
      <h2>{{ card.fr }}</h2>
      <p class="transcription">{{ card.transcription }}</p>
      <p>{{ card.ru }}</p>
      <AudioButton :text="card.audio_text" :label="ui('listen', settings.uiLanguage)" />
    </template>

    <template v-else-if="card.type === 'exercise'">
      <div class="eyebrow">{{ settings.uiLanguage === 'ru' ? 'Упражнение' : 'Exercice' }}</div>
      <ExerciseRenderer
        v-if="exerciseById(card.exercise_id)"
        :lesson-id="lesson.id"
        :exercise="exerciseById(card.exercise_id)"
      />
    </template>
  </article>
</template>
