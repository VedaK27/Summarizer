# syntax=docker/dockerfile:1
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install heavy dependencies first (Cached unless you change versions)
COPY requirements-heavy.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-heavy.txt

# # 2. Download Spacy model (Cached unless spacy version changes)
# RUN python -m spacy download en_core_web_sm

# 3. Install light dependencies (Fast to rebuild)
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt


COPY app ./app

RUN mkdir -p uploads audio outputs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]