import { defineStore } from 'pinia'
import { apiGet } from '../lib/api'

export interface LocalizedText {
  ru: string
  fr: string
}

export interface Profile {
  id: string
  display_name: string
  ui_language: string
  learning_language: string
  voice_id: string
  rank_id: string
  vulgar_library_enabled: boolean
}

export interface Voice {
  id: string
  label: string
  lang: string
  engine: string
  quality: string
}

export interface Section {
  id: string
  slug: string
  order: number
  icon: string
  title: LocalizedText
  subtitle: LocalizedText
  level: string
  tone: string
  lessons: string[]
  is_adult: boolean
}

export interface BootstrapPayload {
  profile: Profile
  progress: Record<string, unknown>
  sections: Section[]
  ranks: Record<string, unknown>[]
  voices: Voice[]
}

export const useBootstrapStore = defineStore('bootstrap', {
  state: () => ({
    payload: null as BootstrapPayload | null,
    loading: false,
    error: null as string | null,
  }),
  actions: {
    async load() {
      if (this.payload || this.loading) return

      this.loading = true
      this.error = null

      try {
        this.payload = await apiGet<BootstrapPayload>('/app/bootstrap')
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
      } finally {
        this.loading = false
      }
    },
  },
})
