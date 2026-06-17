@echo off
cd /d "%~dp0.."
git config user.name "web-lizard"
git config user.email "web-lizard@users.noreply.github.com"
git status --short
git add .
git commit -m "patch 5: edge tts audio drill and cache controls"
git push -u origin main
