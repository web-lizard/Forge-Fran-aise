<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { apiGet } from '../lib/api'
import { t } from '../lib/i18n'
import LessonTile from '../components/learning/LessonTile.vue'
import { useSettingsStore } from '../stores/settingsStore'

const route = useRoute()
const settings = useSettingsStore()
const section = ref<any | null>(null)
const loading = ref(false)

async function loadSection() {
  loading.value = true
  section.value = await apiGet<any>('/course/sections/' + route.params.sectionId)
  loading.value = false
}

onMounted(loadSection)
watch(() => route.params.sectionId, loadSection)
</script>

<template>
  <section class="page">
    <div v-if="loading" class="soft-card">Загрузка...</div>

    <template v-if="section">
      <div class="section-title">
        <div class="eyebrow">{{ section.level }} / {{ section.tone }}</div>
        <h1>{{ t(section.title, settings.uiLanguage) }}</h1>
        <p>{{ t(section.subtitle, settings.uiLanguage) }}</p>
      </div>

      <div class="card-list">
        <LessonTile
          v-for="lesson in section.lesson_items"
          :key="lesson.id"
          :lesson="lesson"
        />
      </div>
    </template>
  </section>
</template>
