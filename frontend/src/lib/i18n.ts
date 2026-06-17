import type { LocalizedText } from '../stores/bootstrapStore'

export function t(value: LocalizedText | undefined, lang: 'ru' | 'fr'): string {
  if (!value) return ''
  return value[lang] || value.ru || value.fr || ''
}

export function ui(label: string, lang: 'ru' | 'fr'): string {
  const dict: Record<string, Record<'ru' | 'fr', string>> = {
    throne: { ru: 'Трон', fr: 'Trône' },
    lessons: { ru: 'Уроки', fr: 'Leçons' },
    drill: { ru: 'Дрель', fr: 'Drill' },
    codex: { ru: 'Кодекс', fr: 'Codex' },
    profile: { ru: 'Профиль', fr: 'Profil' },
    continue: { ru: 'Продолжить', fr: 'Continuer' },
    listen: { ru: 'Слушать', fr: 'Écouter' },
    why: { ru: 'Почему?', fr: 'Pourquoi ?' },
    next: { ru: 'Дальше', fr: 'Suivant' },
    correct: { ru: 'Верно', fr: 'Correct' },
    wrong: { ru: 'Мимо', fr: 'Raté' },
  }

  return dict[label]?.[lang] ?? label
}
