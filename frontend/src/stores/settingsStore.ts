import { defineStore } from 'pinia'
import { apiGet, apiPatch } from '../lib/api'
import { useBootstrapStore } from './bootstrapStore'

export type UiLanguage = 'ru' | 'fr'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    uiLanguage: 'ru' as UiLanguage,
    voiceId: 'mock_fr_female',
    sheetOpen: false,
    sheetTitle: '',
    sheetBody: '',
  }),
  getters: {
    isFrenchUi: (state) => state.uiLanguage === 'fr',
  },
  actions: {
    hydrateFromBootstrap() {
      const bootstrap = useBootstrapStore()
      const profile = bootstrap.payload?.profile

      if (!profile) return

      this.uiLanguage = profile.ui_language as UiLanguage
      this.voiceId = profile.voice_id
    },
    async toggleLanguage() {
      this.uiLanguage = this.uiLanguage === 'ru' ? 'fr' : 'ru'

      const bootstrap = useBootstrapStore()
      const profileId = bootstrap.payload?.profile?.id

      if (profileId) {
        await apiPatch(`/profiles/${profileId}`, {
          ui_language: this.uiLanguage,
        })

        if (bootstrap.payload?.profile) {
          bootstrap.payload.profile.ui_language = this.uiLanguage
        }
      }
    },
    async setVoice(voiceId: string) {
      this.voiceId = voiceId

      const bootstrap = useBootstrapStore()
      const profileId = bootstrap.payload?.profile?.id

      if (profileId) {
        await apiPatch(`/profiles/${profileId}`, {
          voice_id: voiceId,
        })

        if (bootstrap.payload?.profile) {
          bootstrap.payload.profile.voice_id = voiceId
        }
      }
    },
    openSheet(title: string, body: string) {
      this.sheetTitle = title
      this.sheetBody = body
      this.sheetOpen = true
    },
    closeSheet() {
      this.sheetOpen = false
    },
  },
})
