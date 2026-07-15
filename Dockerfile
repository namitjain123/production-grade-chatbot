FROM python:3.12-slim

# libmagic1: required by `unstructured` for file-type detection when parsing docx/pptx
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Bake the FlashRank ONNX reranker model into the image so container startup
# doesn't need to download it on every cold start / new replica.
RUN python -c "from app.services.retrieval.ranking_service import warm_up; warm_up()"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
