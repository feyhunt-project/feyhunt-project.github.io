@echo off
rem Vote Analyzer launcher. Double-click to start on the default port, or pass a port as argument.
cd /d "%~dp0"
set PORT=%1
if "%PORT%"=="" set PORT=8000
title Vote Analyzer (port %PORT%)

rem Find Python: prefer the "py" launcher, fall back to "python"
set PY=py
where py >nul 2>&1 || set PY=python
where %PY% >nul 2>&1 || (echo Python was not found. Install it from python.org and tick "Add to PATH". & pause & exit /b 1)

rem Open the browser after a short delay, in a separate hidden-ish window, so the server below can start first
start "" /min cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:%PORT%"

echo Vote Analyzer is running at http://localhost:%PORT%
echo Close this window or press Ctrl+C to stop the server.
echo.

rem Run the server in THIS window: closing the window stops it
%PY% app.py %PORT%
if errorlevel 1 (echo. & echo The server stopped with an error. Is port %PORT% already in use? Try: start.bat 8001 & pause)
