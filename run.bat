@echo off
title ClanVox - Multilingual Real-Time Voice ^& Chat AI Suite

:: Set working directory to project root
cd /d "%~dp0"

:: Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ===================================================================
    echo  [WARNING] Python Virtual environment not found at .venv\
    echo ===================================================================
    echo  Would you like to automatically create .venv now?
    echo  1. Yes, create .venv and install core requirements
    echo  2. No, exit
    set /p init_choice="Enter choice (1-2): "
    if "%init_choice%"=="1" (
        python -m venv .venv
        .venv\Scripts\python.exe -m pip install fastapi "uvicorn[standard]" pydantic pydantic-settings python-dotenv websockets httpx aiohttp pyyaml anyio python-multipart cachetools jinja2 pyjwt cryptography structlog pytest pytest-asyncio aiosqlite sqlalchemy regex rapidfuzz num2words emoji babel livekit-api
        echo Environment successfully initialized!
        pause
    ) else (
        exit /b 1
    )
)

:menu
cls
echo ===================================================================
echo       CLANVOX - MULTILINGUAL REAL-TIME VOICE ^& CHAT SUITE
echo ===================================================================
echo.
echo  --- SERVERS ^& USER INTERFACES ---
echo   1. Launch ClanVox API ^& Web Server (FastAPI + WebSockets + UI)
echo   2. Open Web Browser Interface (http://localhost:8000/app)
echo   3. Launch Docker Compose Stack (LiveKit, Redis, Postgres/pgvector)
echo.
echo  --- VOICE AGENT ^& PIPELINES ---
echo   4. Launch LiveKit Voice Agent Worker (agent/worker.py)
echo   5. Interactive Multilingual CLI Demo (Hinglish/Code-Switching)
echo.
echo  --- TEST SUITES ^& EVALUATION ---
echo   6. Run All Automated Tests (pytest backend/tests)
echo   7. Test Real-Time WebSocket Endpoint (test_websocket.py)
echo   8. Test Code-Switching ^& Script Splitter (test_codeswitch.py)
echo   9. Test Language Router ^& Hysteresis (test_language_router.py)
echo  10. Test Sentence Chunker ^& Low-Latency Audio Streaming
echo.
echo  --- SETUP ^& DEPENDENCY MANAGEMENT ---
echo  11. Install / Update Core Requirements (requirements.txt)
echo  12. Install Development ^& Testing Tools (requirements-dev.txt)
echo  13. Install Self-Hosted ML Stack (requirements-ml.txt - GPU)
echo.
echo  --- MAINTENANCE ^& DATA CLEANING ---
echo  14. Clean Python Bytecode Trash (__pycache__, *.pyc, *.pytest_cache)
echo  15. Reset Local SQLite Database (clanvox.db)
echo  16. Perform Full Clean (Cache + DB + Temporary Logs)
echo.
echo   0. Exit
echo ===================================================================
set /p choice="Enter your choice (0-16): "

if "%choice%"=="1" goto run_api_server
if "%choice%"=="2" goto open_browser
if "%choice%"=="3" goto run_docker
if "%choice%"=="4" goto run_worker
if "%choice%"=="5" goto run_cli_demo
if "%choice%"=="6" goto run_tests
if "%choice%"=="7" goto test_ws
if "%choice%"=="8" goto test_codeswitch
if "%choice%"=="9" goto test_router
if "%choice%"=="10" goto test_chunker
if "%choice%"=="11" goto install_core
if "%choice%"=="12" goto install_dev
if "%choice%"=="13" goto install_ml
if "%choice%"=="14" goto clean_cache
if "%choice%"=="15" goto clean_db
if "%choice%"=="16" goto full_clean
if "%choice%"=="0" goto end

goto menu

:: ----- RUN SERVER -----

:run_api_server
echo.
echo [SERVER] Starting ClanVox API and Realtime Gateway on http://localhost:8000...
echo [INFO] Web UI available at: http://localhost:8000/app
echo [INFO] Press Ctrl+C to stop the server.
echo.
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
pause
goto menu

:open_browser
echo.
echo [BROWSER] Opening ClanVox UI in default browser...
start http://localhost:8000/app
goto menu

:run_docker
echo.
echo [DOCKER] Launching ClanVox background infrastructure (LiveKit, Redis, Postgres)...
docker compose up -d redis postgres livekit
echo Services launched.
pause
goto menu

:: ----- VOICE AGENT & DEMO -----

:run_worker
echo.
echo [AGENT] Launching LiveKit Real-Time Voice Agent Worker...
.venv\Scripts\python.exe agent\worker.py
pause
goto menu

:run_cli_demo
echo.
.venv\Scripts\python.exe backend\app\cli_demo.py
pause
goto menu

:: ----- TEST SUITES -----

:run_tests
echo.
echo [TESTS] Running complete ClanVox test suite...
.venv\Scripts\python.exe -m pytest backend/tests -v
pause
goto menu

:test_ws
echo.
echo [TESTS] Running WebSocket real-time turn tests...
.venv\Scripts\python.exe -m pytest backend/tests/test_websocket.py -v
pause
goto menu

:test_codeswitch
echo.
echo [TESTS] Running Code-Switching and Script Detection tests...
.venv\Scripts\python.exe -m pytest backend/tests/test_codeswitch.py -v
pause
goto menu

:test_router
echo.
echo [TESTS] Running Language Router hysteresis tests...
.venv\Scripts\python.exe -m pytest backend/tests/test_language_router.py -v
pause
goto menu

:test_chunker
echo.
echo [TESTS] Running Multilingual Sentence Chunker tests...
.venv\Scripts\python.exe -m pytest backend/tests/test_sentence_chunker.py -v
pause
goto menu

:: ----- SETUP & INSTALLATION -----

:install_core
echo.
echo [SETUP] Installing core dependencies from requirements.txt...
.venv\Scripts\python.exe -m pip install -r requirements.txt
pause
goto menu

:install_dev
echo.
echo [SETUP] Installing development dependencies from Requirements/requirements-dev.txt...
.venv\Scripts\python.exe -m pip install -r Requirements/requirements-dev.txt
pause
goto menu

:install_ml
echo.
echo [SETUP] Installing ML and self-hosted models from Requirements/requirements-ml.txt...
.venv\Scripts\python.exe -m pip install -r Requirements/requirements-ml.txt
pause
goto menu

:: ----- CLEANING & MAINTENANCE -----

:clean_cache
echo.
echo [CLEAN] Cleaning Python bytecode cache and pytest cache...
powershell -Command "Get-ChildItem -Path . -Recurse -Include __pycache__, .pytest_cache | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
powershell -Command "Get-ChildItem -Path . -Recurse -Filter *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue"
echo Cache cleaned.
pause
goto menu

:clean_db
echo.
echo [CLEAN] Removing local SQLite database...
if exist "clanvox.db" del /f /q "clanvox.db"
echo Database reset.
pause
goto menu

:full_clean
echo.
echo [CLEAN] Performing full deep clean...
powershell -Command "Get-ChildItem -Path . -Recurse -Include __pycache__, .pytest_cache | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
powershell -Command "Get-ChildItem -Path . -Recurse -Filter *.pyc | Remove-Item -Force -ErrorAction SilentlyContinue"
powershell -Command "Get-ChildItem -Path . -Recurse -Filter *.log | Remove-Item -Force -ErrorAction SilentlyContinue"
if exist "clanvox.db" del /f /q "clanvox.db"
echo Full deep clean completed!
pause
goto menu

:end
echo Exiting ClanVox Suite. Goodbye!
exit /b 0
