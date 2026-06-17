@echo off
echo Backend port 8797:
netstat -ano | findstr ":8797"
echo.
echo Frontend port 5197:
netstat -ano | findstr ":5197"
