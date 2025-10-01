#!/usr/bin/env sh
set -e

echo "[entrypoint] preparando /app/model…"
mkdir -p /app/model

need=0
for f in candidate_embeddings.npy candidate_texts_processed.joblib job_embeddings.npy job_matching_neural_model.pth job_texts_processed.joblib; do
  if [ ! -s "/app/model/$f" ]; then
    echo "[entrypoint] faltando: $f"
    need=1
  fi
done

if [ "$need" = "1" ]; then
  echo "[entrypoint] /app/model incompleto; baixando assets da release v1.0.0…"
  curl -fsSL "https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/candidate_embeddings.npy"           -o /app/model/candidate_embeddings.npy
  curl -fsSL "https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/candidate_texts_processed.joblib"   -o /app/model/candidate_texts_processed.joblib
  curl -fsSL "https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/job_embeddings.npy"                 -o /app/model/job_embeddings.npy
  curl -fsSL "https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/job_matching_neural_model.pth"      -o /app/model/job_matching_neural_model.pth
  curl -fsSL "https://github.com/caiosaldanha/api-vagas/releases/download/v1.0.0/job_texts_processed.joblib"         -o /app/model/job_texts_processed.joblib
  ls -lah /app/model
else
  echo "[entrypoint] modelos já presentes; seguindo."
fi

# opcional: permissões “seguras”
chmod 755 /app/model || true
chmod 644 /app/model/* || true

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"