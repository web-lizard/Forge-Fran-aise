# Forge Française

Имперский мозговыбиватель французского языка.

Mobile-first учебный движок французского языка на Vue 3, FastAPI и JSON-контенте.

## Ports

Backend:
http://127.0.0.1:8797/api/health

Frontend:
http://127.0.0.1:5197

Diagnostics:
http://127.0.0.1:5197/diagnostics

## Быстрый запуск

Через ярлык на рабочем столе:

Forge Francaise

Или вручную:

```cmd
scripts\Forge Francaise Launcher.cmd
```

## Установка зависимостей

```cmd
scripts\install_all.cmd
```

## Проверки

Backend validation and smoke:

```cmd
scripts\check_backend.cmd
```

Frontend build:

```cmd
scripts\check_frontend.cmd
```

Full MVP check:

```cmd
scripts\check_all.cmd
```

Live smoke, когда backend уже запущен:

```cmd
scripts\smoke_live.cmd
```

## Если порты заняты

```cmd
scripts\status_ports.cmd
scripts\kill_ports.cmd
```

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
- diagnostics endpoint
- backend smoke tests
- frontend build checks
- MVP report generator

## Demo Flow

1. Open http://127.0.0.1:5197
2. Press Continue.
3. Listen to a phrase.
4. Open Drill and answer a few questions.
5. Open Audio and test voice selection.
6. Open Profile and switch RU / FR.
7. Open Diagnostics and check counts.

## MVP Report

```cmd
py scripts\mvp_report.py
```

Report appears here:

reports\MVP_REPORT.md

## Patch 6

Patch 6 adds:

- diagnostics API
- diagnostics page
- backend smoke tests
- live smoke tests
- frontend build check script
- install all script
- check all script
- port status and kill scripts
- MVP report generator
- final README
