@echo off
cd /d "%~dp0..\frontend"
call npm run test:e2e:report
