@echo off
set /p VOICE_PID=<"%~dp0work\voice.pid"
taskkill /PID %VOICE_PID% /T /F
pause
