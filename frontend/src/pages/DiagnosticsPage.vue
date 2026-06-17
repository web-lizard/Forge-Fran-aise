<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { apiGet } from '../lib/api'
import { useSettingsStore } from '../stores/settingsStore'

const settings = useSettingsStore()
const diagnostics = ref<any | null>(null)
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''

  try {
    diagnostics.value = await apiGet('/diagnostics')
  } catch (exc) {
    error.value = exc instanceof Error ? exc.message : String(exc)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <section class="page">
    <div class="section-title compact-title">
      <div class="eyebrow">Diagnostics</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Диагностика MVP' : 'Diagnostic MVP' }}</h1>
      <p>
        {{
          settings.uiLanguage === 'ru'
            ? 'Проверяем, что контент, API, аудио-кэш и прогресс живые.'
            : 'Vérification du contenu, de l’API, du cache audio et de la progression.'
        }}
      </p>
    </div>

    <div v-if="loading" class="soft-card">Загрузка...</div>
    <div v-if="error" class="soft-card danger-card">{{ error }}</div>

    <template v-if="diagnostics">
      <article class="study-card">
        <h2>Application</h2>
        <div class="diagnostic-grid">
          <div>
            <span>Version</span>
            <strong>{{ diagnostics.app.version }}</strong>
          </div>
          <div>
            <span>Backend</span>
            <strong>{{ diagnostics.app.backend_port }}</strong>
          </div>
          <div>
            <span>Frontend</span>
            <strong>{{ diagnostics.app.frontend_port }}</strong>
          </div>
        </div>
      </article>

      <article class="study-card">
        <h2>Content</h2>
        <div class="stat-grid">
          <div>
            <strong>{{ diagnostics.content.sections }}</strong>
            <span>sections</span>
          </div>
          <div>
            <strong>{{ diagnostics.content.lessons }}</strong>
            <span>lessons</span>
          </div>
          <div>
            <strong>{{ diagnostics.content.exercises }}</strong>
            <span>drill</span>
          </div>
        </div>
        <div class="stat-grid">
          <div>
            <strong>{{ diagnostics.content.codex_entries }}</strong>
            <span>codex</span>
          </div>
          <div>
            <strong>{{ diagnostics.content.vulgar_items }}</strong>
            <span>vulgar</span>
          </div>
          <div>
            <strong>{{ diagnostics.progress_summary.score }}</strong>
            <span>score</span>
          </div>
        </div>
      </article>

      <article class="study-card">
        <h2>Audio cache</h2>
        <div class="stat-grid">
          <div>
            <strong>{{ diagnostics.audio_cache.count }}</strong>
            <span>files</span>
          </div>
          <div>
            <strong>{{ diagnostics.audio_cache.total_mb }}</strong>
            <span>mb</span>
          </div>
          <div>
            <strong>{{ diagnostics.audio_cache.indexed_count }}</strong>
            <span>indexed</span>
          </div>
        </div>
      </article>

      <article class="study-card">
        <h2>Paths</h2>
        <div v-for="(item, key) in diagnostics.paths" :key="key" class="codex-row">
          <strong>{{ key }}</strong>
          <span>{{ item.exists ? 'ok' : 'missing' }}</span>
          <small>{{ item.path }}</small>
        </div>
      </article>

      <button class="primary-button" type="button" @click="load">
        {{ settings.uiLanguage === 'ru' ? 'Обновить' : 'Rafraîchir' }}
      </button>
    </template>
  </section>
</template>
