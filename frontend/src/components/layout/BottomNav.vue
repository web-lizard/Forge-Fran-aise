<script setup lang="ts">
import { useSettingsStore } from '../../stores/settingsStore'

const settings = useSettingsStore()
</script>

<template>
  <nav class="bottom-nav">
    <RouterLink to="/">{{ settings.uiLanguage === 'ru' ? 'Трон' : 'Trône' }}</RouterLink>
    <RouterLink to="/campaign">{{ settings.uiLanguage === 'ru' ? 'Уроки' : 'Leçons' }}</RouterLink>
    <RouterLink to="/practice">{{ settings.uiLanguage === 'ru' ? 'Дрель' : 'Drill' }}</RouterLink>
    <RouterLink to="/audio">{{ settings.uiLanguage === 'ru' ? 'Аудио' : 'Audio' }}</RouterLink>
    <RouterLink to="/profile">{{ settings.uiLanguage === 'ru' ? 'Профиль' : 'Profil' }}</RouterLink>
  </nav>
</template>
