@echo off
cd /d "%~dp0"
if exist "dist\SheldonTwitching Labels.exe" (
  start "" "dist\SheldonTwitching Labels.exe" --headless
) else (
  start "SheldonTwitching Labels Bridge" /min py app.py --headless
)
echo Local bridge started; use http://127.0.0.1:47831/overlay in OBS.
