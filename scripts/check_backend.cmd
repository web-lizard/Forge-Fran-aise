@echo off
cd /d "%~dp0..\backend"

if not exist ".venv" (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt

echo.
echo Content validation...
python scripts\validate_content.py
if errorlevel 1 exit /b 1

echo.
echo Backend smoke...
python scripts\smoke_backend.py
if errorlevel 1 exit /b 1

echo.
echo Audio config smoke...
python scripts\smoke_audio_config.py
if errorlevel 1 exit /b 1
