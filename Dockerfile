# syntax=docker/dockerfile:1.6
FROM python:3.10-slim AS app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_COLOR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ARG INSTALL_DEV=false

# + curl/ca-certificates para o entrypoint baixar os modelos
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgomp1 curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-input --prefer-binary --no-cache-dir -r requirements.txt

ARG INSTALL_DEV
RUN if [ "$INSTALL_DEV" = "true" ]; then \
      pip install --no-input --prefer-binary --no-cache-dir \
        pytest==7.4.3 pytest-cov==4.1.0 pytest-asyncio==0.21.1 ; \
    fi

# código da app
COPY app/ ./app/

# não copie a pasta model do repositório (ela vai ser preenchida no start)
# COPY model/ ./model/   <-- REMOVA/COMENTE se existir

# logs e porta
RUN mkdir -p /app/logs
EXPOSE 8000

# entrypoint idempotente
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]