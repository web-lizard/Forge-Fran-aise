<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import AudioButton from '../components/learning/AudioButton.vue'
import RankBadge from '../components/imperial/RankBadge.vue'
import { apiGet } from '../lib/api'
import { ui } from '../lib/i18n'
import { useBootstrapStore } from '../stores/bootstrapStore'
import { useSettingsStore } from '../stores/settingsStore'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()
const summary = ref<any | null>(null)

onMounted(async () => {
  await bootstrap.load()
  settings.hydrateFromBootstrap()
  summary.value = await apiGet('/progress/local_lizard/summary')
})

const profile = computed(() => bootstrap.payload?.profile)
const firstLesson = computed(() => bootstrap.payload?.sections?.[0]?.lessons?.[0] ?? 'greetings_001')
</script>

<template>
  <section class="page throne-page">
    <div class="hero-card">
      <div class="crest-orb">♛</div>
      <div class="eyebrow">Forge Française</div>
      <h1>{{ settings.uiLanguage === 'ru' ? 'Тронный зал' : 'Salle du trône' }}</h1>
      <p>
        {{
          settings.uiLanguage === 'ru'
            ? 'Мобильная имперская кузница французского. Без перегруза, но с короной.'
            : 'Une forge mobile et impériale pour apprendre le français.'
        }}
      </p>

      <div class="profile-strip" v-if="profile">
        <span>{{ profile.display_name }}</span>
        <strong>{{ profile.rank_id }}</strong>
      </div>

      <RankBadge
        v-if="profile"
        :rank-id="profile.rank_id"
        :score="summary?.score ?? 0"
      />

      <div class="stat-grid" v-if="summary">
        <div>
          <strong>{{ summary.score }}</strong>
          <span>score</span>
        </div>
        <div>
          <strong>{{ summary.accuracy }}%</strong>
          <span>accuracy</span>
        </div>
        <div>
          <strong>{{ summary.completed_count }}</strong>
          <span>lessons</span>
        </div>
      </div>

      <div class="hero-actions">
        <RouterLink class="primary-button" :to="'/lesson/' + firstLesson">
          {{ ui('continue', settings.uiLanguage) }}
        </RouterLink>
        <AudioButton text="Bonjour, monsieur." :label="ui('listen', settings.uiLanguage)" />
      </div>
    </div>

    <div class="quick-grid">
      <RouterLink class="quick-card" to="/practice">
        <strong>{{ settings.uiLanguage === 'ru' ? 'Дрель' : 'Drill' }}</strong>
        <span>{{ settings.uiLanguage === 'ru' ? '5 быстрых ударов по хаосу' : 'Cinq coups rapides contre le chaos' }}</span>
      </RouterLink>

      <RouterLink class="quick-card" to="/audio">
        <strong>{{ settings.uiLanguage === 'ru' ? 'Аудио' : 'Audio' }}</strong>
        <span>{{ settings.uiLanguage === 'ru' ? 'Слушать, повторять, запоминать' : 'Écouter, répéter, retenir' }}</span>
      </RouterLink>

      <RouterLink class="quick-card" to="/vulgar">
        <strong>{{ settings.uiLanguage === 'ru' ? 'Мат' : 'Gros mots' }}</strong>
        <span>{{ settings.uiLanguage === 'ru' ? 'Грубый французский под замком' : 'Français vulgaire sous contrôle' }}</span>
      </RouterLink>

      <RouterLink class="quick-card" to="/diagnostics">
        <strong>{{ settings.uiLanguage === 'ru' ? 'Диагностика' : 'Diagnostic' }}</strong>
        <span>{{ settings.uiLanguage === 'ru' ? 'Проверить, жив ли мозговыбиватель' : 'Vérifier le moteur' }}</span>
      </RouterLink>
    </div>
  </section>
</template>
