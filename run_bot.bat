@echo off
REM Me Helper bot — auto-restart wrapper.
REM If the process crashes (network, unhandled error), it restarts after 5 seconds.

cd /d "C:\Me_helper\bot"

:loop
echo [%date% %time%] Starting Me Helper bot...
"C:\Me_helper\.venv\Scripts\python.exe" main.py
echo [%date% %time%] Bot exited with code %errorlevel%. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto loop
