<script setup lang="ts">
defineProps<{
  rankId?: string
  score?: number
}>()
</script>

<template>
  <div class="rank-badge">
    <span>Grade</span>
    <strong>{{ rankId ?? 'recrue' }}</strong>
    <small>{{ score ?? 0 }} score</small>
  </div>
</template>
