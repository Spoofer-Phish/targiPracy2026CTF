@echo off
rem Starts KRAKNAUTICA 2099. Set the organiser password below (or leave it to get a random one).
rem set CTF_ADMIN_PASSWORD=change-me
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  py app.py
) else (
  python app.py
)
pause
