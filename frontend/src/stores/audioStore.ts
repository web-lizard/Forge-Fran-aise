import { defineStore } from 'pinia'
import { apiDelete, apiGet, apiPost, publicApiUrl } from '../lib/api'
import { useSettingsStore } from './settingsStore'

export const useAudioStore = defineStore('audio', {
  state: () => ({
    cache: null as any | null,
    loading: false,
    error: null as string | null,
    lastResult: null as any | null,
  }),
  actions: {
    async loadCache() {
      this.loading = true
      this.error = null

      try {
        this.cache = await apiGet('/audio/cache')
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
      } finally {
        this.loading = false
      }
    },
    async clearCache() {
      this.loading = true
      this.error = null

      try {
        await apiDelete('/audio/cache')
        await this.loadCache()
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
      } finally {
        this.loading = false
      }
    },
    async speak(text: string, mode = 'normal') {
      const settings = useSettingsStore()
      this.loading = true
      this.error = null

      try {
        const result = await apiPost<any>('/audio/speak', {
          text,
          lang: 'fr',
          voice_id: settings.voiceId,
          speed: mode === 'slow' ? 0.75 : 1,
          mode,
        })

        this.lastResult = result
        const audio = new Audio(publicApiUrl(result.url))
        await audio.play()
        return result
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
        throw error
      } finally {
        this.loading = false
      }
    },
  },
})
