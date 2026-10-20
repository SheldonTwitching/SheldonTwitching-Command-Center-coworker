@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (
  echo Python was not found. Install Python 3.11+ and ensure it is on PATH.
  pause
  exit /b 1
)
py -m pip install -r requirements-windows.txt
if errorlevel 1 (
  echo Dependency installation failed.
  pause
  exit /b 1
)
py tools\stamp_build.py 2.0.0
py -m PyInstaller --noconfirm --clean --onefile --windowed --version-file installer/version_info.txt --name "SheldonTwitching - Command Center" --add-data "web;web" --add-data "assets;assets" --add-data "scenes;scenes" --add-data "arcade;arcade" --add-data "streamlabs-tip-goal;streamlabs-tip-goal" --collect-all webview --collect-all pystray --collect-all tzdata --icon "assets\ST-Command-Center.ico" app.py
if errorlevel 1 (
  echo EXE build failed.
  pause
  exit /b 1
)
echo.
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" installer\CommandCenter.iss
echo Build complete! Look for: dist\SheldonTwitching - Command Center.exe
echo Windows WebView2 runtime may be required on older systems.
pause
