<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { apiPost } from '../../lib/api'
import { t, ui } from '../../lib/i18n'
import { useSettingsStore } from '../../stores/settingsStore'
import AudioButton from '../learning/AudioButton.vue'

const props = defineProps<{
  lessonId: string
  exercise: any
  autoFocus?: boolean
}>()

const emit = defineEmits<{
  answered: [payload: any]
}>()

const settings = useSettingsStore()

const selected = ref('')
const textAnswer = ref('')
const builtParts = ref<string[]>([])
const result = ref<any | null>(null)
const loading = ref(false)

const exerciseType = computed(() => props.exercise?.type ?? 'choose_option')
const builtAnswer = computed(() => builtParts.value.join(' ').replace(' ,', ',').replace(' .', '.'))

watch(
  () => props.exercise?.id,
  () => {
    selected.value = ''
    textAnswer.value = ''
    builtParts.value = []
    result.value = null
    loading.value = false
  }
)

async function submit(value: string) {
  loading.value = true

  try {
    result.value = await apiPost('/practice/answer', {
      profile_id: 'local_lizard',
      lesson_id: props.lessonId,
      exercise_id: props.exercise.id,
      answer: value,
    })

    emit('answered', result.value)
  } finally {
    loading.value = false
  }
}

function choose(value: string) {
  selected.value = value
  submit(value)
}

function addPart(value: string) {
  builtParts.value.push(value)
}

function undoPart() {
  builtParts.value.pop()
}

function submitBuilt() {
  submit(builtAnswer.value)
}

function submitText() {
  submit(textAnswer.value)
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

    <template v-if="exerciseType === 'fill_blank'">
      <input
        v-model="textAnswer"
        class="answer-input"
        type="text"
        autocomplete="off"
        placeholder="..."
        @keyup.enter="submitText"
      />
      <button class="primary-button" type="button" :disabled="loading || !textAnswer.trim()" @click="submitText">
        {{ settings.uiLanguage === 'ru' ? 'Ответить' : 'Répondre' }}
      </button>
    </template>

    <template v-else-if="exerciseType === 'phrase_builder'">
      <div class="built-phrase">
        <span v-if="builtParts.length">{{ builtAnswer }}</span>
        <span v-else class="muted">{{ settings.uiLanguage === 'ru' ? 'Собери фразу из блоков' : 'Construis la phrase' }}</span>
      </div>

      <div class="option-grid">
        <button
          v-for="option in exercise.options"
          :key="option"
          class="option-button"
          type="button"
          :disabled="loading"
          @click="addPart(option)"
        >
          {{ option }}
        </button>
      </div>

      <div class="button-row">
        <button class="ghost-button" type="button" :disabled="loading || !builtParts.length" @click="undoPart">
          ←
        </button>
        <button class="primary-button" type="button" :disabled="loading || !builtParts.length" @click="submitBuilt">
          {{ settings.uiLanguage === 'ru' ? 'Проверить' : 'Vérifier' }}
        </button>
      </div>
    </template>

    <template v-else>
      <div class="option-grid">
        <button
          v-for="option in exercise.options"
          :key="option"
          class="option-button"
          :class="{ selected: selected === option }"
          type="button"
          :disabled="loading"
          @click="choose(option)"
        >
          {{ option }}
        </button>
      </div>
    </template>

    <div v-if="result" class="result-box" :class="{ good: result.correct, bad: !result.correct }">
      <strong>{{ result.correct ? ui('correct', settings.uiLanguage) : ui('wrong', settings.uiLanguage) }}</strong>
      <p>{{ t(result.explanation, settings.uiLanguage) }}</p>
      <small>Score: {{ result.score }}</small>
    </div>
  </div>
</template>
