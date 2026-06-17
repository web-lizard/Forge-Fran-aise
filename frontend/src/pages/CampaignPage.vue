<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiGet } from '../lib/api'
import { t } from '../lib/i18n'
import { useSettingsStore } from '../stores/settingsStore'

const settings = useSettingsStore()
const course = ref<any | null>(null)

onMounted(async () => {
  course.value = await apiGet<any>('/course')
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Campagne</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Учебные секции' : 'Sections' }}</h1>
      <p v-if="course">
        {{ course.total_sections }} sections / {{ course.total_lessons }} lessons
      </p>
    </div>

    <div class="card-list">
      <RouterLink
        v-for="section in course?.sections ?? []"
        :key="section.id"
        class="lesson-tile"
        :to="section.id === 'vulgar_french' ? '/vulgar' : '/section/' + section.id"
      >
        <div class="tile-icon">{{ section.icon }}</div>
        <div>
          <strong>{{ t(section.title, settings.uiLanguage) }}</strong>
          <span>{{ t(section.subtitle, settings.uiLanguage) }}</span>
          <small>{{ section.lesson_items.length }} lessons</small>
        </div>
      </RouterLink>
    </div>
  </section>
</template>
