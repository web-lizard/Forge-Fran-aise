<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import AudioButton from '../components/learning/AudioButton.vue'
import { useBootstrapStore } from '../stores/bootstrapStore'
import { useSettingsStore } from '../stores/settingsStore'
import { ui } from '../lib/i18n'

const bootstrap = useBootstrapStore()
const settings = useSettingsStore()

onMounted(async () => {
  await bootstrap.load()
  settings.hydrateFromBootstrap()
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

      <RouterLink class="quick-card" to="/vulgar">
        <strong>{{ settings.uiLanguage === 'ru' ? 'Мат' : 'Gros mots' }}</strong>
        <span>{{ settings.uiLanguage === 'ru' ? 'Грубый французский под замком' : 'Français vulgaire sous contrôle' }}</span>
      </RouterLink>

      <RouterLink class="quick-card" to="/codex">
        <strong>{{ ui('codex', settings.uiLanguage) }}</strong>
        <span>{{ settings.uiLanguage === 'ru' ? 'Артикли, de и прочая магия' : 'Articles, de et autres mystères' }}</span>
      </RouterLink>
    </div>
  </section>
</template>
