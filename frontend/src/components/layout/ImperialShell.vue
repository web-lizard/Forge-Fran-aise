<script setup lang="ts">
import BottomNav from './BottomNav.vue'
import TopBar from './TopBar.vue'
import BottomSheet from './BottomSheet.vue'
</script>

<template>
  <div class="imperial-shell">
    <div class="flying-layer" aria-hidden="true">
      <span>é</span>
      <span>ç</span>
      <span>à</span>
      <span>œ</span>
    </div>

    <TopBar />

    <main class="shell-main">
      <slot />
    </main>

    <BottomNav />
    <BottomSheet />
  </div>
</template>
