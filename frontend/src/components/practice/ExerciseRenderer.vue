<script setup lang="ts">
import { ref } from 'vue'
import { apiPost } from '../../lib/api'
import { t, ui } from '../../lib/i18n'
import { useSettingsStore } from '../../stores/settingsStore'
import AudioButton from '../learning/AudioButton.vue'

const props = defineProps<{
  lessonId: string
  exercise: any
}>()

const settings = useSettingsStore()
const selected = ref('')
const result = ref<any | null>(null)
const loading = ref(false)

async function answer(value: string) {
  selected.value = value
  loading.value = true

  try {
    result.value = await apiPost('/practice/answer', {
      profile_id: 'local_lizard',
      lesson_id: props.lessonId,
      exercise_id: props.exercise.id,
      answer: value,
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="exercise-renderer">
    <h2>{{ t(exercise.prompt, settings.uiLanguage) }}</h2>

    <AudioButton
      v-if="exercise.audio_text"
      :text="exercise.audio_text"
      :label="ui('listen', settings.uiLanguage)"
    />

    <div class="option-grid">
      <button
        v-for="option in exercise.options"
        :key="option"
        class="option-button"
        :class="{ selected: selected === option }"
        type="button"
        :disabled="loading"
        @click="answer(option)"
      >
        {{ option }}
      </button>
    </div>

    <div v-if="result" class="result-box" :class="{ good: result.correct, bad: !result.correct }">
      <strong>{{ result.correct ? ui('correct', settings.uiLanguage) : ui('wrong', settings.uiLanguage) }}</strong>
      <p>{{ t(result.explanation, settings.uiLanguage) }}</p>
    </div>
  </div>
</template>
