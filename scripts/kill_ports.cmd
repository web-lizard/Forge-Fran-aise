@echo off
echo Killing processes on ports 8797 and 5197 if any...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8797"') do (
  taskkill /PID %%a /F
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5197"') do (
  taskkill /PID %%a /F
)

echo Done.
