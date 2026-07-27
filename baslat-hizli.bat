@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0backend"
title Sekine (hizli mod)

if not exist ".venv\Scripts\python.exe" (
  echo [Sekine] Sanal ortam kuruluyor...
  py -3 -m venv .venv 2>nul || python -m venv .venv
)
call ".venv\Scripts\activate.bat"

if not exist ".venv\.deps_min" (
  echo [Sekine] Hafif paketler kuruluyor...
  python -m pip install --upgrade pip
  pip install -r requirements-min.txt
  type nul > ".venv\.deps_min"
)

set SEKINE_EMBEDDER=hash
echo.
echo [Sekine] HIZLI MOD - eslestirme kalitesi dusuk, arayuz/akis/grafik tam calisir.
echo [Sekine] Sunucu: http://localhost:8000  (kapatmak icin Ctrl+C)
timeout /t 2 >nul
start "" http://localhost:8000
uvicorn app:app --port 8000
pause
