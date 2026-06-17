import type { Page, Route } from '@playwright/test'

const profile = {
  id: 'local_lizard',
  display_name: 'Monsieur Souveraineté',
  ui_language: 'ru',
  learning_language: 'fr',
  voice_id: 'edge_fr_denise',
  rank_id: 'recrue',
  vulgar_library_enabled: true,
}

const progressSummary = {
  profile_id: 'local_lizard',
  score: 120,
  current_level: 'A0',
  completed_lessons: [],
  completed_count: 0,
  total_answers: 3,
  correct_answers: 2,
  wrong_answers: 1,
  accuracy: 67,
  weak_topics: ['article', 'audio'],
  tag_stats: [],
  recent_events: [],
}

const sections = [
  {
    id: 'start',
    slug: 'start',
    order: 0,
    icon: 'crown',
    title: { ru: 'Вход во французский', fr: 'Entrée dans le français' },
    subtitle: { ru: 'Приветствия, вежливость и первые фразы.', fr: 'Salutations et premières phrases.' },
    level: 'A0',
    tone: 'basic',
    lessons: ['greetings_001'],
    is_adult: false,
  },
  {
    id: 'articles',
    slug: 'articles',
    order: 2,
    icon: 'shield',
    title: { ru: 'Артикли', fr: 'Les articles' },
    subtitle: { ru: 'Le, la, les без тумана.', fr: 'Le, la, les.' },
    level: 'A0',
    tone: 'grammar',
    lessons: ['le_la_001'],
    is_adult: false,
  },
  {
    id: 'vulgar_french',
    slug: 'vulgar-french',
    order: 7,
    icon: 'flame',
    title: { ru: 'Французский мат', fr: 'Les gros mots français' },
    subtitle: { ru: 'Грубые фразы и регистр.', fr: 'Registre vulgaire.' },
    level: 'A1',
    tone: 'vulgar',
    lessons: ['vulgar_intro_001'],
    is_adult: true,
  },
]

const ranks = [
  {
    id: 'recrue',
    order: 1,
    fr: 'Recrue',
    transcription: '[рёкрю]',
    ru: 'новобранец',
    min_score: 0,
  },
  {
    id: 'soldat',
    order: 2,
    fr: 'Soldat',
    transcription: '[сольда]',
    ru: 'солдат',
    min_score: 100,
  },
]

const voices = [
  {
    id: 'edge_fr_denise',
    label: 'Denise Neural, France',
    lang: 'fr',
    engine: 'edge',
    quality: 'neural-online',
    gender: 'female',
  },
  {
    id: 'mock_fr_female',
    label: 'Voix impériale féminine, mock',
    lang: 'fr',
    engine: 'mock',
    quality: 'dev',
    gender: 'female',
  },
]

const greetingLesson = {
  id: 'greetings_001',
  section_id: 'start',
  order: 1,
  level: 'A0',
  title: {
    ru: 'Bonjour, merci и базовая вежливость',
    fr: 'Bonjour, merci et la politesse de base',
  },
  cards: [
    {
      type: 'theory',
      title: { ru: 'Первый принцип', fr: 'Premier principe' },
      body: {
        ru: 'Сначала учим короткие живые фразы.',
        fr: 'On commence par des phrases courtes.',
      },
    },
    {
      type: 'word',
      fr: 'Bonjour',
      transcription: '[бонжур]',
      ru: 'здравствуйте / добрый день',
      audio_text: 'Bonjour',
      tooltip: {
        ru: 'Универсальное вежливое приветствие.',
        fr: 'Salutation polie.',
      },
    },
    {
      type: 'exercise',
      exercise_id: 'ex_bonjour_translation',
    },
  ],
  exercises: [
    {
      id: 'ex_bonjour_translation',
      type: 'choose_option',
      lesson_id: 'greetings_001',
      section_id: 'start',
      prompt: {
        ru: 'Что значит Bonjour?',
        fr: 'Que signifie Bonjour ?',
      },
      options: ['спасибо', 'здравствуйте', 'пожалуйста', 'до свидания'],
      answer: 'здравствуйте',
      explanation: {
        ru: 'Bonjour значит здравствуйте или добрый день.',
        fr: 'Bonjour signifie bonjour.',
      },
      audio_text: 'Bonjour',
      tags: ['greeting', 'basic'],
      difficulty: 1,
    },
  ],
}

const leLaLesson = {
  id: 'le_la_001',
  section_id: 'articles',
  order: 1,
  level: 'A0',
  title: {
    ru: 'Le и la',
    fr: 'Le et la',
  },
  cards: [
    {
      type: 'word',
      fr: 'la maison',
      transcription: '[ля мэзон]',
      ru: 'дом',
      audio_text: 'la maison',
      tooltip: {
        ru: 'maison женского рода.',
        fr: 'maison est féminin.',
      },
    },
    {
      type: 'exercise',
      exercise_id: 'ex_la_maison_001',
    },
  ],
  exercises: [
    {
      id: 'ex_la_maison_001',
      type: 'choose_option',
      lesson_id: 'le_la_001',
      section_id: 'articles',
      prompt: {
        ru: 'Выбери правильный артикль: ___ maison',
        fr: 'Choisis le bon article : ___ maison',
      },
      options: ['le', 'la', 'les'],
      answer: 'la',
      explanation: {
        ru: 'maison женского рода, поэтому la maison.',
        fr: 'maison est féminin, donc la maison.',
      },
      audio_text: 'la maison',
      tags: ['article', 'gender'],
      difficulty: 1,
    },
  ],
}

const course = {
  sections: sections.map((section) => ({
    ...section,
    lesson_items: [
      {
        id: section.lessons[0],
        section_id: section.id,
        order: 1,
        level: section.level,
        title: section.id === 'articles' ? leLaLesson.title : greetingLesson.title,
        card_count: 3,
        exercise_count: 1,
      },
    ],
  })),
  total_sections: sections.length,
  total_lessons: sections.length,
}

const diagnostics = {
  ok: true,
  app: {
    app_name: 'Forge Francaise',
    version: '0.7.0',
    backend_port: 8797,
    frontend_port: 5197,
  },
  content: {
    sections: 8,
    lessons: 13,
    exercises: 17,
    vulgar_items: 6,
    codex_entries: 4,
  },
  paths: {
    project_root: { path: 'mock', exists: true, is_dir: true },
    content_root: { path: 'mock/content', exists: true, is_dir: true },
  },
  frontend: {
    package_json: true,
    index_html: true,
    src: true,
    env_local: true,
  },
  backend: {
    requirements: true,
    main: true,
    venv: true,
  },
  audio_cache: {
    count: 1,
    indexed_count: 1,
    total_bytes: 1024,
    total_mb: 0.001,
    items: [],
  },
  progress_summary: progressSummary,
}

function json(route: Route, body: unknown, status = 200) {
  return route.fulfill({
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  })
}

function courseSection(sectionId: string) {
  const section = course.sections.find((item) => item.id === sectionId || item.slug === sectionId)
  return section ?? course.sections[0]
}

function lessonById(lessonId: string) {
  if (lessonId === 'le_la_001') return leLaLesson
  return greetingLesson
}

export async function installMockApi(page: Page) {
  await page.addInitScript(() => {
    ;(window as any).__speechCalls = []

    const fakeSpeech = {
      cancel: () => {},
      speak: (utterance: SpeechSynthesisUtterance) => {
        ;(window as any).__speechCalls.push(utterance.text)
      },
      getVoices: () => [],
    }

    Object.defineProperty(window, 'speechSynthesis', {
      value: fakeSpeech,
      configurable: true,
    })
  })

  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    let path = url.pathname

    const apiIndex = path.indexOf('/api')
    if (apiIndex >= 0) {
      path = path.slice(apiIndex + 4) || '/'
    }

    if (request.method() === 'PATCH' && path.startsWith('/profiles/')) {
      return json(route, profile)
    }

    if (request.method() === 'DELETE' && path === '/audio/cache') {
      return json(route, { ok: true, removed: 1 })
    }

    if (request.method() === 'POST' && path === '/audio/speak') {
      return json(route, {
        audio_id: 'mock-audio',
        url: '/api/audio/file/mock-audio',
        cached: false,
        duration_ms: 600,
        provider: 'mock',
        format: 'wav',
        fallback: true,
      })
    }

    if (request.method() === 'POST' && path === '/practice/answer') {
      return json(route, {
        correct: true,
        expected: 'здравствуйте',
        explanation: {
          ru: 'Тестовый ответ засчитан.',
          fr: 'Réponse acceptée.',
        },
        score: 130,
        weak_topics: [],
      })
    }

    if (path.startsWith('/audio/file/')) {
      return route.fulfill({
        status: 200,
        contentType: 'audio/wav',
        body: '',
      })
    }

    if (path === '/health') return json(route, { ok: true, app: 'forge-francaise' })
    if (path === '/settings') return json(route, { app_name: 'Forge Francaise', version: '0.7.0' })
    if (path === '/diagnostics') return json(route, diagnostics)
    if (path === '/app/bootstrap') {
      return json(route, {
        profile,
        progress: progressSummary,
        sections,
        ranks,
        voices,
      })
    }

    if (path === '/course') return json(route, course)

    if (path.startsWith('/course/sections/')) {
      const sectionId = decodeURIComponent(path.split('/').pop() ?? 'start')
      return json(route, courseSection(sectionId))
    }

    if (path.startsWith('/lessons/')) {
      const lessonId = decodeURIComponent(path.split('/').pop() ?? 'greetings_001')
      return json(route, lessonById(lessonId))
    }

    if (path === '/codex') {
      return json(route, [
        {
          id: 'articles',
          title: { ru: 'Артикли', fr: 'Les articles' },
          summary: { ru: 'Тестовая статья.', fr: 'Article de test.' },
          items: [
            { fr: 'le', transcription: '[лё]', ru: 'артикль мужского рода' },
          ],
        },
      ])
    }

    if (path === '/vulgar/items') {
      return json(route, [
        {
          id: 'putain_j_en_ai_marre',
          fr: 'Putain, j’en ai marre.',
          transcription: '[пютэн, жанэ мар]',
          ru: 'Блядь, меня это достало.',
          rudeness_level: 4,
          context: { ru: 'Грубо.', fr: 'Vulgaire.' },
          audio_text: 'Putain, j’en ai marre.',
          tags: ['vulgar'],
          softer_versions: [
            { fr: 'J’en ai assez.', transcription: '[жанэ асэ]', ru: 'Мне хватит.' },
          ],
        },
      ])
    }

    if (path === '/audio/voices') return json(route, voices)
    if (path === '/audio/cache') {
      return json(route, {
        count: 1,
        indexed_count: 1,
        total_bytes: 1024,
        total_mb: 0.001,
        items: [],
      })
    }

    if (path.startsWith('/progress/local_lizard/summary')) return json(route, progressSummary)
    if (path.startsWith('/progress/local_lizard')) return json(route, progressSummary)

    if (path.startsWith('/review/local_lizard/session')) {
      return json(route, {
        profile_id: 'local_lizard',
        mode: url.searchParams.get('mode') ?? 'quick',
        limit: Number(url.searchParams.get('limit') ?? 7),
        count: 2,
        exercises: [
          {
            ...greetingLesson.exercises[0],
            lesson_id: 'greetings_001',
            section_id: 'start',
            lesson_title: greetingLesson.title,
            level: 'A0',
          },
          {
            ...leLaLesson.exercises[0],
            lesson_id: 'le_la_001',
            section_id: 'articles',
            lesson_title: leLaLesson.title,
            level: 'A0',
          },
        ],
      })
    }

    return json(route, { ok: true, path })
  })
}
