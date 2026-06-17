<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { apiGet } from '../lib/api'
import { useSettingsStore } from '../stores/settingsStore'
import ExerciseRenderer from '../components/practice/ExerciseRenderer.vue'

const settings = useSettingsStore()
const lesson = ref<any | null>(null)

const exercise = computed(() => lesson.value?.exercises?.[0] ?? null)

onMounted(async () => {
  lesson.value = await apiGet<any>('/lessons/le_la_001')
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Drill</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Один удар по хаосу' : 'Un coup contre le chaos' }}</h1>
    </div>

    <div v-if="lesson && exercise" class="study-card">
      <ExerciseRenderer :lesson-id="lesson.id" :exercise="exercise" />
    </div>
  </section>
</template>
