# Forge Française MVP Report

Generated: 2026-06-17T09:10:00

## Status

- Version: 0.6.0
- Backend: http://127.0.0.1:8797/api/health
- Frontend: http://127.0.0.1:5197
- Git commit: 834ed4e
- Git dirty: yes

## Content

- Sections: 8
- Lessons: 13
- Exercises: 17
- Codex entries: 4
- Vulgar items: 6

## Sections

- start: Вход во французский / Entrée dans le français
- pronunciation: Произношение / Prononciation
- articles: Артикли / Les articles
- de_du: De, du, de la / De, du, de la
- nouns: Род и число / Genre et nombre
- verbs: Базовые глаголы / Verbes de base
- phrasebook: Фразовый арсенал / Arsenal de phrases
- vulgar_french: Французский мат / Les gros mots français

## MVP Features

- Vue 3 + TypeScript + Vite frontend
- FastAPI backend
- JSON content engine
- content validation
- mobile-first UI
- bottom navigation
- one-card lesson flow
- practice modes
- progress scoring
- weak topic review
- audio drill
- Edge TTS provider with mock fallback
- audio cache API
- RU / FR interface switch
- voice selector
- vulgar French library
- diagnostics endpoint
- smoke tests
- build scripts

## Demo Flow

1. Open http://127.0.0.1:5197
2. Continue the first lesson.
3. Open drill and answer several questions.
4. Open audio drill and test Edge voice.
5. Open profile and switch voice / language.
6. Open diagnostics.

## Check Commands

```cmd
scripts\check_backend.cmd
scripts\check_frontend.cmd
scripts\check_all.cmd
```
