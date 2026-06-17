# Forge Française

Имперский мозговыбиватель французского языка.

Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

## Ports

Backend:
http://127.0.0.1:8797/api/health

Frontend:
http://127.0.0.1:5197

## Быстрый запуск

scripts\Forge Francaise Launcher.cmd

## Что уже заложено

- Vue 3 + TypeScript + Vite
- FastAPI backend
- JSON content engine
- profiles / progress / ranks
- TTS provider architecture
- edge-tts provider
- mock fallback provider
- audio cache API
- audio drill page
- vulgar French library
- mobile-first UI
- bottom navigation
- bottom sheet
- RU / FR UI switch
- voice selector
- storage adapter
- scalable ExerciseRenderer
- course API
- section pages
- lesson card mode
- expanded A0 content
- real practice sessions
- weak topic review
- progress scoring
- answer event log

## Patch 5

Patch 5 adds:

- edge-tts dependency
- EdgeTTSProvider
- MP3 audio generation
- mock fallback if Edge TTS fails
- audio cache index
- GET /api/audio/cache
- DELETE /api/audio/cache
- AudioDrillPage
- /audio route
- stronger VoiceSelector
- audio cache controls in profile
- bottom nav audio entry

Edge voices require internet. If they fail, app falls back to mock.
