@echo off
cd /d "%~dp0"
if exist "dist\SheldonTwitching Labels.exe" (
  start "" "dist\SheldonTwitching Labels.exe"
) else (
  py app.py
)
