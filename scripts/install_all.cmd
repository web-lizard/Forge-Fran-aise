@echo off
cd /d "%~dp0.."

echo.
echo Installing backend deps...
cd /d "%~dp0..\backend"

if not exist ".venv" (
  py -m venv .venv
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Installing frontend deps...
cd /d "%~dp0..\frontend"
npm install

echo.
echo INSTALL ALL DONE
