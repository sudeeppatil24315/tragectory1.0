@echo off
echo Keeping Llama 3.1 8B loaded in GPU memory...
echo This will prevent the 5-6 second load time on first request.
echo.
echo Press Ctrl+C to stop
echo.

ollama run llama3.1:8b
