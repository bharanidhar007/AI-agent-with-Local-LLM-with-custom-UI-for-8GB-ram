@echo off
rem One-command launcher for Windows.
cd /d "%~dp0"

if "%DEFAULT_MODEL%"=="" set DEFAULT_MODEL=llama3.2:3b

where ollama >nul 2>nul
if errorlevel 1 (
  echo Ollama is not installed. Get it from https://ollama.com/download and run this again.
  pause
  exit /b 1
)

rem Start Ollama if the server isn't answering.
ollama list >nul 2>nul
if errorlevel 1 (
  echo Starting Ollama...
  start "" /B ollama serve
  timeout /t 5 >nul
)

rem Download the default model the first time.
ollama list | findstr /C:"%DEFAULT_MODEL%" >nul
if errorlevel 1 (
  echo Downloading %DEFAULT_MODEL% ^(one-time, about 2 GB^)...
  ollama pull %DEFAULT_MODEL%
)

if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt

start "" http://127.0.0.1:8000
python server.py
