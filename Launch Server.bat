@echo off
rem Website Launcher. Double-click to start on default port or pass port as argument.
cd /d "%~dp0"
set PORT=%1
if "%PORT%"=="" set PORT=8000
title Voting Website (port %PORT%)

rem Start the HTTP server in the background using start /b
start /b py -m http.server %PORT% >nul 2>&1 || start /b python -m http.server %PORT% >nul 2>&1

rem Wait for 1.5 seconds to let the server catch up (ping localhost 2 times takes ~1 second, or use timeout)
timeout /t 1 /nobreak >nul

rem Open the browser
start http://localhost:%PORT%

echo Voting Website is running at http://localhost:%PORT%
echo Close this window or press Ctrl+C to stop the server.
echo.

rem Keep the script alive so the server doesn't instantly close
pause >nul