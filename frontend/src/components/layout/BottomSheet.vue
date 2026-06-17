<script setup lang="ts">
import { useSettingsStore } from '../../stores/settingsStore'

const settings = useSettingsStore()
</script>

<template>
  <Teleport to="body">
    <div v-if="settings.sheetOpen" class="sheet-backdrop" @click="settings.closeSheet">
      <section class="bottom-sheet" @click.stop>
        <div class="sheet-handle"></div>
        <div class="sheet-head">
          <h2>{{ settings.sheetTitle }}</h2>
          <button class="ghost-button" type="button" @click="settings.closeSheet">×</button>
        </div>
        <p>{{ settings.sheetBody }}</p>
      </section>
    </div>
  </Teleport>
</template>
