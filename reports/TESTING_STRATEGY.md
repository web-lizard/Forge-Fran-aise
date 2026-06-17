# Forge Française Testing Strategy

## What this catches

- Vite red overlay and parser errors.
- BOM in JSON / TS / Vue / CSS / HTML files.
- Broken main routes.
- Missing main UI.
- Buttons and links with zero size.
- Buttons and links covered by another element.
- Horizontal overflow on mobile.
- Audio button click path.
- Audio button stuck disabled/loading state.
- Browser speech fallback path.
- Practice answer flow.
- Frontend build failure.
- Backend API smoke failure.
- Default profile accidentally using mock voice.

## Main command

```cmd
scripts\test_guard.cmd
```

## Faster UI-only command

```cmd
scripts\test_guard_fast.cmd
```

## Open Playwright report

```cmd
scripts\playwright_report.cmd
```
