# syntax=docker/dockerfile:1.6
FROM python:3.10-slim AS app

# Qualidade de vida do pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_COLOR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Se precisar instalar deps de teste: --build-arg INSTALL_DEV=true
ARG INSTALL_DEV=false

# Dependências de runtime e ferramentas p/ baixar modelos
RUN apt-get update && apt-get install -y --no-install-recommends \
      libgomp1 \
      curl \
      ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Copie apenas o requirements para maximizar cache
COPY requirements.txt .

# 2) Instale as deps com cache do pip entre builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-input --prefer-binary --no-cache-dir -r requirements.txt

# 3) (Opcional) deps de teste quando INSTALL_DEV=true
ARG INSTALL_DEV
RUN if [ "$INSTALL_DEV" = "true" ]; then \
      pip install --no-input --prefer-binary --no-cache-dir \
        pytest==7.4.3 pytest-cov==4.1.0 pytest-asyncio==0.21.1 ; \
    fi

# 4) Copie o código
COPY app/ ./app/

# 5) Baixe os modelos da release v1.0.0 para /app/model
ARG MODEL_URL_CAND_EMB="https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/candidate_embeddings.npy"
ARG MODEL_URL_CAND_TXT="https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/candidate_texts_processed.joblib"
ARG MODEL_URL_JOB_EMB="https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/job_embeddings.npy"
ARG MODEL_URL_NEURAL="https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/job_matching_neural_model.pth"
ARG MODEL_URL_JOB_TXT="https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/job_texts_processed.joblib"

RUN mkdir -p /app/model \
 && curl -fL "$MODEL_URL_CAND_EMB" -o /app/model/candidate_embeddings.npy \
 && curl -fL "$MODEL_URL_CAND_TXT" -o /app/model/candidate_texts_processed.joblib \
 && curl -fL "$MODEL_URL_JOB_EMB" -o /app/model/job_embeddings.npy \
 && curl -fL "$MODEL_URL_NEURAL" -o /app/model/job_matching_neural_model.pth \
 && curl -fL "$MODEL_URL_JOB_TXT" -o /app/model/job_texts_processed.joblib \
 && ls -lah /app/model

# 6) Logs e porta
RUN mkdir -p /app/logs
EXPOSE 8000

# 7) Comando (ouve fora do container)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]