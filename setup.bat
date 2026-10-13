@echo off
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

if "%OLLAMA_CHAT_MODEL%"=="" set OLLAMA_CHAT_MODEL=qwen2.5vl:3b
if "%OLLAMA_EMBEDDING_MODEL%"=="" set OLLAMA_EMBEDDING_MODEL=nomic-embed-text

echo ==========================================
echo  DyslexiaLearn Local AI Setup ^(Windows^)
echo ==========================================
echo.

echo --^> Checking prerequisites
where node >nul 2>nul
if errorlevel 1 (
  echo [missing] Node.js
  echo Install from https://nodejs.org/
  exit /b 1
)
echo [ok] node

where python >nul 2>nul
if errorlevel 1 (
  echo [missing] Python
  echo Install from https://www.python.org/downloads/ and add Python to PATH.
  exit /b 1
)
echo [ok] python

where curl >nul 2>nul
if errorlevel 1 (
  echo [missing] curl
  echo Install curl or use a modern Windows version that includes it.
  exit /b 1
)
echo [ok] curl

where ollama >nul 2>nul
if errorlevel 1 (
  echo [missing] Ollama
  echo Install from https://ollama.com/
  exit /b 1
)
echo [ok] ollama

where piper >nul 2>nul
if errorlevel 1 (
  echo [missing] Piper TTS
  echo Install Piper and add it to PATH so backend speech works.
  exit /b 1
)
echo [ok] piper

where pnpm >nul 2>nul
if errorlevel 1 (
  where npm >nul 2>nul
  if errorlevel 1 (
    echo [missing] npm
    echo Install Node.js from https://nodejs.org/
    exit /b 1
  )
  set PACKAGE_MANAGER=npm
) else (
  set PACKAGE_MANAGER=pnpm
)
echo [ok] frontend package manager: %PACKAGE_MANAGER%

where docker >nul 2>nul
if errorlevel 1 (
  set DOCKER_AVAILABLE=0
  echo [optional missing] docker
  echo Install Docker Desktop if you want the script to start PostgreSQL.
) else (
  set DOCKER_AVAILABLE=1
  echo [ok] docker
)

echo.
echo --^> Installing backend dependencies
cd /d "%ROOT_DIR%backend"
if not exist "venv" (
  python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
call venv\Scripts\deactivate.bat

echo.
echo --^> Installing frontend dependencies
cd /d "%ROOT_DIR%frontend"
if "%PACKAGE_MANAGER%"=="pnpm" (
  pnpm install
) else (
  npm install
)

echo.
echo --^> Starting PostgreSQL with Docker, if available
cd /d "%ROOT_DIR%"
if "%DOCKER_AVAILABLE%"=="1" (
  docker compose version >nul 2>nul
  if errorlevel 1 (
    docker-compose -f docker\docker-compose.yml up -d
  ) else (
    docker compose -f docker\docker-compose.yml up -d
  )
  if errorlevel 1 echo [warn] Docker database did not start. Check Docker Desktop.
) else (
  echo [skip] Docker unavailable. Use your own PostgreSQL or update backend\.env.
)

echo.
echo --^> Checking Ollama
curl -s http://localhost:11434/api/tags >nul 2>nul
if errorlevel 1 (
  echo [warn] Ollama is installed but not responding at localhost:11434.
  echo Start Ollama manually if model pulls fail.
) else (
  echo [ok] Ollama is running
)

echo.
echo --^> Pulling local AI models
ollama pull %OLLAMA_CHAT_MODEL%
if errorlevel 1 echo [warn] Could not pull %OLLAMA_CHAT_MODEL%.
ollama pull %OLLAMA_EMBEDDING_MODEL%
if errorlevel 1 echo [warn] Could not pull %OLLAMA_EMBEDDING_MODEL%.

echo.
echo --^> Downloading Piper voices
if not exist "backend\tts\voices" mkdir "backend\tts\voices"
powershell -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$base='https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0';" ^
  "$out='backend/tts/voices';" ^
  "$voices=@(@('en/en_US/lessac/medium','en_US-lessac-medium.onnx'),@('en/en_US/amy/medium','en_US-amy-medium.onnx'),@('en/en_US/ryan/medium','en_US-ryan-medium.onnx'),@('en/en_GB/alan/medium','en_GB-alan-medium.onnx'));" ^
  "foreach($v in $voices){$url=\"$base/$($v[0])/$($v[1])?download=true\"; $json=\"$url.json\"; Write-Host \"Downloading $($v[1])\"; Invoke-WebRequest -Uri $url -OutFile \"$out/$($v[1])\"; Invoke-WebRequest -Uri $json -OutFile \"$out/$($v[1]).json\";}"
if errorlevel 1 (
  echo [warn] Piper voices failed to download. You can rerun setup later.
)

echo.
echo --^> Writing backend local environment
if not exist "backend\.env" copy "backend\.env.example" "backend\.env" >nul
powershell -ExecutionPolicy Bypass -Command ^
  "$path='backend/.env';" ^
  "$embedding='%OLLAMA_EMBEDDING_MODEL%'; if($embedding -notmatch ':'){$embedding=\"$embedding`:latest\"};" ^
  "$values=@{OLLAMA_CHAT_MODEL='%OLLAMA_CHAT_MODEL%'; OLLAMA_EMBEDDING_MODEL=$embedding; TTS_ENGINE='piper'; PIPER_BINARY_PATH='piper'; PIPER_VOICE_DIR='tts/voices'};" ^
  "$lines=Get-Content $path;" ^
  "$seen=@{}; $next=@();" ^
  "foreach($line in $lines){$key=($line -split '=',2)[0]; if($values.ContainsKey($key)){$next += \"$key=$($values[$key])\"; $seen[$key]=$true}else{$next += $line}}" ^
  "foreach($key in $values.Keys){if(-not $seen.ContainsKey($key)){$next += \"$key=$($values[$key])\"}}" ^
  "Set-Content -Path $path -Value $next"

echo.
echo ==========================================
echo  Setup complete.
echo ==========================================
echo.
echo Start backend:
echo   cd backend ^&^& venv\Scripts\activate ^&^& uvicorn app.main:app --reload --port 8080
echo.
echo Start frontend:
if "%PACKAGE_MANAGER%"=="pnpm" (
  echo   cd frontend ^&^& pnpm dev
) else (
  echo   cd frontend ^&^& npm run dev
)
echo.
echo Quality profile:
echo   OLLAMA_CHAT_MODEL=%OLLAMA_CHAT_MODEL%
echo   TTS_ENGINE=piper
pause
