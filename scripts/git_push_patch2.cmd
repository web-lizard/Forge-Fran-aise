@echo off
cd /d "%~dp0.."
git status --short
git add .
git commit -m "patch 2: ux settings launcher and scalable frontend"
git push -u origin main
