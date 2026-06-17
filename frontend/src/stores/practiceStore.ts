import { defineStore } from 'pinia'
import { apiGet } from '../lib/api'

export type PracticeMode = 'quick' | 'weak' | 'audio' | 'vulgar' | 'articles'

export const usePracticeStore = defineStore('practice', {
  state: () => ({
    mode: 'quick' as PracticeMode,
    session: null as any | null,
    currentIndex: 0,
    loading: false,
    error: null as string | null,
    answered: 0,
    correct: 0,
  }),
  getters: {
    currentExercise: (state) => state.session?.exercises?.[state.currentIndex] ?? null,
    total: (state) => state.session?.exercises?.length ?? 0,
    finished: (state) => Boolean(state.session && state.currentIndex >= (state.session.exercises?.length ?? 0)),
    accuracy: (state) => state.answered ? Math.round(state.correct / state.answered * 100) : 0,
  },
  actions: {
    async load(mode: PracticeMode = this.mode) {
      this.mode = mode
      this.loading = true
      this.error = null
      this.currentIndex = 0
      this.answered = 0
      this.correct = 0

      try {
        this.session = await apiGet(`/review/local_lizard/session?mode=${mode}&limit=7`)
      } catch (error) {
        this.error = error instanceof Error ? error.message : String(error)
      } finally {
        this.loading = false
      }
    },
    markAnswered(payload: any) {
      this.answered += 1
      if (payload?.correct) {
        this.correct += 1
      }
    },
    next() {
      if (!this.session) return
      this.currentIndex += 1
    },
  },
})
