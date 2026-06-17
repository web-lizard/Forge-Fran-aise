<script setup lang="ts">
import { onMounted } from 'vue'
import { useBootstrapStore } from '../../stores/bootstrapStore'
import { useSettingsStore } from '../../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()

onMounted(async () => {
  await bootstrap.load()
  settings.hydrateFromBootstrap()
})
</script>

<template>
  <header class="top-bar">
    <div>
      <div class="eyebrow">Forge Française</div>
      <div class="top-title">Имперский мозговыбиватель</div>
    </div>

    <button class="ghost-button" type="button" @click="settings.toggleLanguage">
      {{ settings.uiLanguage.toUpperCase() }}
    </button>
  </header>
</template>
