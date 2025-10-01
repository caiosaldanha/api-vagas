# syntax=docker/dockerfile:1.6
FROM python:3.10-slim AS app

# Qualidade de vida do pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_COLOR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Se precisar instalar deps de teste: --build-arg INSTALL_DEV=true
ARG INSTALL_DEV=false

# Dependência de runtime do PyTorch (OpenMP)
# (não precisa de gcc/g++ se usamos wheels binários)
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgomp1 \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Copie apenas o requirements para maximizar cache
COPY requirements.txt .

# 2) Instale as deps com cache do pip entre builds
#    --no-cache-dir mantém a imagem final enxuta; o cache vem do mount (não vai pra camada)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-input --prefer-binary --no-cache-dir -r requirements.txt

# 3) Opcional: deps de teste quando INSTALL_DEV=true
RUN if [ "$INSTALL_DEV" = "true" ]; then \
      echo "Instalando deps de teste..." && \
      --mount=type=cache,target=/root/.cache/pip \
      pip install --no-input --prefer-binary --no-cache-dir \
        pytest==7.4.3 pytest-cov==4.1.0 pytest-asyncio==0.21.1 ; \
    fi

# 4) Agora copie o código (não invalida a camada de deps)
COPY app/ ./app/
COPY model/ ./model/

# 5) Logs e porta
RUN mkdir -p /app/logs
EXPOSE 8000

# 6) Comando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]