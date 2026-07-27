# Keşf — Hugging Face Spaces (Docker)
# Hafif "fastembed / ONNX" yolu: torch YOK, ~220 MB model, 512 MB RAM'e sığar.
FROM python:3.11-slim

WORKDIR /app

# 1) Bağımlılıklar (önce sadece requirements → Docker katman cache'i)
COPY requirements-deploy.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-deploy.txt

# 2) Uygulama kodu + veri (content.json / taxonomy.json)
COPY backend/  ./backend/
COPY frontend/ ./frontend/
COPY data/     ./data/

# 3) fastembed'i seç + yazılabilir cache/db dizinleri
#    (HF Spaces konteyneri uid 1000 ile çalışır; bu yüzden 777)
ENV SEKINE_EMBEDDER=fastembed \
    FASTEMBED_CACHE_PATH=/app/.cache/fastembed \
    HF_HOME=/app/.cache
RUN mkdir -p /app/.cache/fastembed && chmod -R 777 /app/.cache /app/data

# 4) Modeli imaja göm → ilk istek beklemez (aksi halde ilk /api/match'te ~1 dk iner)
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')" && \
    chmod -R 777 /app/.cache

EXPOSE 7860
WORKDIR /app/backend
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
