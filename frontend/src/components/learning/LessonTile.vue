<script setup lang="ts">
import { t } from '../../lib/i18n'
import { useSettingsStore } from '../../stores/settingsStore'

defineProps<{
  lesson: any
}>()

const settings = useSettingsStore()
</script>

<template>
  <RouterLink class="lesson-tile lesson-tile-vertical" :to="'/lesson/' + lesson.id">
    <div class="lesson-meta">
      <span>{{ lesson.level }}</span>
      <span>{{ lesson.card_count }} cards</span>
      <span>{{ lesson.exercise_count }} drill</span>
    </div>
    <strong>{{ t(lesson.title, settings.uiLanguage) }}</strong>
  </RouterLink>
</template>
