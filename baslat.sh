#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"
[ -d .venv ] || python3 -m venv .venv
source .venv/bin/activate
if [ ! -f .venv/.deps_full ]; then
  echo "[Sekine] Paketler kuruluyor (ilk sefer birkaç dakika, torch iniyor)..."
  python -m pip install --upgrade pip
  pip install -r requirements.txt
  touch .venv/.deps_full
fi
echo "[Sekine] Sunucu: http://localhost:8000  (kapatmak için Ctrl+C)"
( sleep 2; command -v open >/dev/null && open http://localhost:8000 || (command -v xdg-open >/dev/null && xdg-open http://localhost:8000) ) &
exec uvicorn app:app --port 8000
