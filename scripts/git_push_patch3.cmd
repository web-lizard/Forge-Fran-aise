@echo off
cd /d "%~dp0.."
git config user.name "web-lizard"
git config user.email "web-lizard@users.noreply.github.com"
git init
git branch -M main
git remote set-url origin https://github.com/web-lizard/Forge-Fran-aise.git
git status --short
git add .
git commit -m "patch 3: course content and lesson navigation"
git push -u origin main
