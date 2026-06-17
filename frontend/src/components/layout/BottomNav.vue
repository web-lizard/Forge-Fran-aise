<script setup lang="ts">
import { ui } from '../../lib/i18n'
import { useSettingsStore } from '../../stores/settingsStore'

const settings = useSettingsStore()
</script>

<template>
  <nav class="bottom-nav">
    <RouterLink to="/">{{ ui('throne', settings.uiLanguage) }}</RouterLink>
    <RouterLink to="/campaign">{{ ui('lessons', settings.uiLanguage) }}</RouterLink>
    <RouterLink to="/practice">{{ ui('drill', settings.uiLanguage) }}</RouterLink>
    <RouterLink to="/codex">{{ ui('codex', settings.uiLanguage) }}</RouterLink>
    <RouterLink to="/profile">{{ ui('profile', settings.uiLanguage) }}</RouterLink>
  </nav>
</template>
