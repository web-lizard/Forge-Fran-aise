@echo off
cd /d "%~dp0..\frontend"

call npm install
call npx playwright install chromium
call npm run test:e2e:headed
