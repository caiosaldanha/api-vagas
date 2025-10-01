"""
API FastAPI para Matching de Vagas com Deep Learning e NLP
"""
import os
import logging
import numpy as np
import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import joblib
from sentence_transformers import SentenceTransformer
import re
import string
from datetime import datetime
import json
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Métricas Prometheus
PREDICTION_REQUESTS = Counter('prediction_requests_total', 'Total prediction requests')
PREDICTION_DURATION = Histogram('prediction_duration_seconds', 'Prediction duration')
PREDICTION_ERRORS = Counter('prediction_errors_total', 'Total prediction errors')
ML_SCORE_GAUGE = Gauge('prediction_ml_score_avg', 'Average ML score of predictions')
MATCH_RATE_GAUGE = Gauge('prediction_match_rate', 'Rate of successful matches')
PROCESSING_TIME_GAUGE = Gauge('prediction_processing_time_ms', 'Processing time in milliseconds')

# Modelo da rede neural (mesmo do notebook)
class JobCandidateMatchingNet(nn.Module):
    def __init__(self, embedding_dim=384, hidden_dim=256):
        super(JobCandidateMatchingNet, self).__init__()
        input_dim = embedding_dim * 2
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, candidate_embedding, job_embedding):
        combined = torch.cat([candidate_embedding, job_embedding], dim=1)
        output = self.layers(combined)
        return output

# Modelos Pydantic para request/response
class CandidateData(BaseModel):
    cv_pt: Optional[str] = ""
    cv_en: Optional[str] = ""
    objetivo_profissional: Optional[str] = ""
    conhecimentos_tecnicos: Optional[str] = ""

class JobData(BaseModel):
    titulo_vaga: Optional[str] = ""
    objetivo_vaga: Optional[str] = ""
    principais_atividades: Optional[str] = ""
    competencia_tecnicas_e_comportamentais: Optional[str] = ""

class PredictionRequest(BaseModel):
    candidate: CandidateData
    jobs: List[JobData]
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)

class JobMatch(BaseModel):
    job_index: int
    similarity_score: float
    ml_score: float
    job_preview: str

class PredictionResponse(BaseModel):
    candidate_processed_text: str
    recommendations: List[JobMatch]
    processing_time_ms: float
    timestamp: str

# Classe para carregar e gerenciar modelos
class ModelManager:
    def __init__(self, model_dir: str = "model"):
        self.model_dir = model_dir
        # Forçar uso de CPU para ambiente enxuto
        self.device = torch.device('cpu')
        logger.info(f"Usando dispositivo: {self.device}")
        self.load_models()
    
    def load_models(self):
        """Carrega apenas os arquivos serializados para predição"""
        try:
            # Sentence transformer apenas para inferência
            logger.info("Carregando Sentence Transformer para inferência...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

            # Rede neural treinada (apenas para predição)
            logger.info("Carregando modelo neural para predição...")
            self.neural_model = JobCandidateMatchingNet(embedding_dim=384)
            model_path = os.path.join(self.model_dir, 'job_matching_neural_model.pth')
            self.neural_model.load_state_dict(torch.load(model_path, map_location='cpu'))
            self.neural_model.to('cpu')
            self.neural_model.eval()

            # Embeddings e textos processados
            logger.info("Carregando embeddings e textos processados...")
            self.candidate_embeddings = np.load(os.path.join(self.model_dir, 'candidate_embeddings.npy'))
            self.job_embeddings = np.load(os.path.join(self.model_dir, 'job_embeddings.npy'))
            self.candidate_texts = joblib.load(os.path.join(self.model_dir, 'candidate_texts_processed.joblib'))
            self.job_texts = joblib.load(os.path.join(self.model_dir, 'job_texts_processed.joblib'))

            logger.info("Arquivos para predição carregados com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao carregar arquivos de predição: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """Pré-processamento de texto igual ao notebook"""
        if not text or not isinstance(text, str):
            return ""
        
        # Converter para minúsculas
        text = text.lower()
        
        # Remover pontuação
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remover números
        text = re.sub(r'\d+', '', text)
        
        # Remover espaços extras
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_candidate_text(self, candidate: CandidateData) -> str:
        """Extrai e combina textos do candidato"""
        texts = []
        
        if candidate.cv_pt:
            texts.append(candidate.cv_pt)
        if candidate.cv_en:
            texts.append(candidate.cv_en)
        if candidate.objetivo_profissional:
            texts.append(candidate.objetivo_profissional)
        if candidate.conhecimentos_tecnicos:
            texts.append(candidate.conhecimentos_tecnicos)
        
        combined_text = ' '.join([str(text) for text in texts if text and str(text).strip()])
        return self.preprocess_text(combined_text)
    
    def extract_job_text(self, job: JobData) -> str:
        """Extrai e combina textos da vaga"""
        texts = []
        
        if job.titulo_vaga:
            texts.append(job.titulo_vaga)
        if job.objetivo_vaga:
            texts.append(job.objetivo_vaga)
        if job.principais_atividades:
            texts.append(job.principais_atividades)
        if job.competencia_tecnicas_e_comportamentais:
            texts.append(job.competencia_tecnicas_e_comportamentais)
        
        combined_text = ' '.join([str(text) for text in texts if text and str(text).strip()])
        return self.preprocess_text(combined_text)
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """Gera embedding para um texto"""
        if not text or len(text.strip()) == 0:
            text = "texto vazio"
        
        embedding = self.sentence_model.encode([text], device=self.device)
        return embedding[0]
    
    def predict_match(self, candidate_embedding: np.ndarray, job_embedding: np.ndarray) -> float:
        """Prediz match usando rede neural"""
        candidate_tensor = torch.FloatTensor(candidate_embedding).unsqueeze(0).to(self.device)
        job_tensor = torch.FloatTensor(job_embedding).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            score = self.neural_model(candidate_tensor, job_tensor).cpu().numpy()[0][0]
        
        return float(score)
    
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calcula similaridade coseno"""
        from sklearn.metrics.pairwise import cosine_similarity
        
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        return float(similarity)

model_manager = ModelManager()

app = FastAPI(
    title="Job Matching API",
    description="API para matching de vagas usando Deep Learning e NLP (apenas predição, sem treinamento)",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Endpoint de health check"""
    return {
        "message": "Job Matching API",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check detalhado"""
    return {
        "status": "healthy",
        "device": str(model_manager.device),
        "models_loaded": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def get_metrics():
    """Endpoint para métricas Prometheus"""
    from fastapi import Response
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict", response_model=PredictionResponse)
async def predict_job_matches(request: PredictionRequest):
    """
    Endpoint principal para predição de matches entre candidato e vagas
    """
    PREDICTION_REQUESTS.inc()  # Incrementar contador
    
    start_time = datetime.now()
    
    try:
        with PREDICTION_DURATION.time():  # Medir duração
            logger.info(f"Processando request com {len(request.jobs)} vagas")
        
        # Extrair e processar texto do candidato
        candidate_text = model_manager.extract_candidate_text(request.candidate)
        
        if not candidate_text or len(candidate_text.strip()) == 0:
            raise HTTPException(
                status_code=400, 
                detail="Dados do candidato insuficientes para análise"
            )
        
        # Gerar embedding do candidato
        candidate_embedding = model_manager.generate_embedding(candidate_text)
        
        # Processar cada vaga e calcular scores
        recommendations = []
        
        for idx, job in enumerate(request.jobs):
            # Extrair texto da vaga
            job_text = model_manager.extract_job_text(job)
            
            if not job_text or len(job_text.strip()) == 0:
                continue
            
            # Gerar embedding da vaga
            job_embedding = model_manager.generate_embedding(job_text)
            
            # Calcular similaridade coseno
            similarity_score = model_manager.calculate_similarity(candidate_embedding, job_embedding)
            
            # Calcular score do modelo neural
            ml_score = model_manager.predict_match(candidate_embedding, job_embedding)
            
            # Aplicar threshold
            if ml_score >= request.threshold:
                recommendations.append(JobMatch(
                    job_index=idx,
                    similarity_score=similarity_score,
                    ml_score=ml_score,
                    job_preview=job_text[:200] + "..." if len(job_text) > 200 else job_text
                ))
        
        # Ordenar por score do modelo neural (decrescente)
        recommendations.sort(key=lambda x: x.ml_score, reverse=True)
        
        # Limitar ao top_k
        recommendations = recommendations[:request.top_k]
        
        # Calcular tempo de processamento
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Log da operação
        logger.info(f"Processamento concluído: {len(recommendations)} matches encontrados em {processing_time:.2f}ms")
        
        # Atualizar métricas Prometheus
        ML_SCORE_GAUGE.set(np.mean([r.ml_score for r in recommendations]) if recommendations else 0)
        MATCH_RATE_GAUGE.set(len(recommendations) / len(request.jobs) if request.jobs else 0)
        PROCESSING_TIME_GAUGE.set(processing_time)
        
        # Registrar para monitoramento
        log_prediction_metrics(
            n_jobs=len(request.jobs),
            n_matches=len(recommendations),
            processing_time_ms=processing_time,
            avg_ml_score=np.mean([r.ml_score for r in recommendations]) if recommendations else 0,
            threshold=request.threshold
        )
        
        return PredictionResponse(
            candidate_processed_text=candidate_text[:500] + "..." if len(candidate_text) > 500 else candidate_text,
            recommendations=recommendations,
            processing_time_ms=processing_time,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        PREDICTION_ERRORS.inc()  # Incrementar contador de erros
        logger.error(f"Erro durante predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

def log_prediction_metrics(n_jobs: int, n_matches: int, processing_time_ms: float, 
                          avg_ml_score: float, threshold: float):
    """Log métricas para monitoramento"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "n_jobs": n_jobs,
        "n_matches": n_matches,
        "processing_time_ms": processing_time_ms,
        "avg_ml_score": avg_ml_score,
        "threshold": threshold,
        "match_rate": n_matches / n_jobs if n_jobs > 0 else 0
    }
    
    # Log estruturado para coleta por ferramentas de monitoramento
    logger.info(f"PREDICTION_METRICS: {json.dumps(metrics)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)