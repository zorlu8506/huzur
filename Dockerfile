# Keşf — Render / HF Spaces (Docker)
# API embedding yolu: model sunucuda TUTULMAZ (Gemini API). Uygulama ~80 MB,
# 512 MB RAM'e rahat sığar, soğuk başlangıç anında. GEMINI_API_KEY host panelinde
# secret olarak verilir (imaja gömülmez).
FROM python:3.11-slim

WORKDIR /app

# 1) Bağımlılıklar (önce sadece requirements → Docker katman cache'i)
COPY requirements-deploy.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-deploy.txt

# 2) Uygulama kodu + veri (content.json / taxonomy.json / seed_vectors.json)
COPY backend/  ./backend/
COPY frontend/ ./frontend/
COPY data/     ./data/

# 3) API embedder'ı seç + yazılabilir db dizini
#    (HF Spaces konteyneri uid 1000 ile çalışır; bu yüzden 777)
ENV SEKINE_EMBEDDER=jina \
    PYTHONUNBUFFERED=1
RUN chmod -R 777 /app/data

# Render $PORT verir; HF Spaces'te ise tanımsız → 7860'a düşer.
EXPOSE 7860
WORKDIR /app/backend
CMD uvicorn app:app --host 0.0.0.0 --port ${PORT:-7860}
