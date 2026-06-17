@echo off
cd /d "%~dp0..\frontend"

if not exist ".env.local" (
  echo VITE_API_BASE=http://127.0.0.1:8797/api> .env.local
)

call npm install
call npm run dev
