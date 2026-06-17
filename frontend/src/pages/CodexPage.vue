<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiGet } from '../lib/api'

const entries = ref<any[]>([])

onMounted(async () => {
  entries.value = await apiGet<any[]>('/codex')
})
</script>

<template>
  <section class="page">
    <div class="section-title">
      <div class="eyebrow">Кодекс</div>
      <h1>Справочник</h1>
    </div>

    <article v-for="entry in entries" :key="entry.id" class="study-card">
      <h2>{{ entry.title.ru }}</h2>
      <p>{{ entry.summary.ru }}</p>

      <div v-for="item in entry.items" :key="item.fr" class="codex-row">
        <strong>{{ item.fr }}</strong>
        <span>{{ item.transcription }}</span>
        <span>{{ item.ru }}</span>
      </div>
    </article>
  </section>
</template>
