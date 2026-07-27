@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0backend"
title Sekine

if not exist ".venv\Scripts\python.exe" (
  echo [Sekine] Sanal ortam kuruluyor...
  py -3 -m venv .venv 2>nul || python -m venv .venv
)
call ".venv\Scripts\activate.bat"

if not exist ".venv\.deps_full" (
  echo [Sekine] Paketler kuruluyor. Ilk sefer birkac dakika surebilir ^(torch iniyor^)...
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  if errorlevel 1 (
    echo.
    echo [HATA] Kurulum basarisiz. Once "baslat-hizli.bat" ile deneyebilirsin.
    pause
    exit /b 1
  )
  type nul > ".venv\.deps_full"
)

echo.
echo [Sekine] Sunucu baslatiliyor: http://localhost:8000
echo [Sekine] Kapatmak icin bu pencerede Ctrl+C.
timeout /t 2 >nul
start "" http://localhost:8000
uvicorn app:app --port 8000
pause
