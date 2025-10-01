"""
Testes unitários para a API de Job Matching
"""
import pytest
import numpy as np
import torch
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import json
import os
import tempfile

# Importar a aplicação
from app.main import app, ModelManager, JobCandidateMatchingNet
from app.main import CandidateData, JobData, PredictionRequest

class TestJobCandidateMatchingNet:
    """Testes para a rede neural"""
    
    def test_model_initialization(self):
        """Testa inicialização do modelo"""
        model = JobCandidateMatchingNet(embedding_dim=384, hidden_dim=256)
        assert model is not None
        
        # Verificar camadas
        assert len(model.layers) == 8  # 4 Linear + 3 ReLU + 1 Dropout + 1 Sigmoid
    
    def test_model_forward_pass(self):
        """Testa forward pass do modelo"""
        model = JobCandidateMatchingNet(embedding_dim=384, hidden_dim=256)
        
        # Dados de teste
        candidate_emb = torch.randn(1, 384)
        job_emb = torch.randn(1, 384)
        
        # Forward pass
        output = model(candidate_emb, job_emb)
        
        # Verificações
        assert output.shape == (1, 1)
        assert 0 <= output.item() <= 1  # Sigmoid output

class TestModelManager:
    """Testes para o gerenciador de modelos"""
    
    @pytest.fixture
    def mock_model_manager(self):
        """Fixture para mock do ModelManager"""
        with patch('app.main.SentenceTransformer'), \
             patch('app.main.torch.load'), \
             patch('app.main.np.load'), \
             patch('app.main.joblib.load'):
            
            manager = ModelManager(model_dir="test_model")
            
            # Mock dos modelos
            manager.sentence_model = Mock()
            manager.neural_model = Mock()
            manager.candidate_embeddings = np.random.rand(100, 384)
            manager.job_embeddings = np.random.rand(50, 384)
            manager.candidate_texts = [{"candidate_id": "1", "text": "test"}]
            manager.job_texts = [{"job_id": "1", "text": "test"}]
            
            return manager
    
    def test_preprocess_text(self, mock_model_manager):
        """Testa pré-processamento de texto"""
        text = "Desenvolvedor Python com 5 anos de experiência!"
        processed = mock_model_manager.preprocess_text(text)
        
        # Verificações
        assert processed.islower()
        assert "!" not in processed  # Pontuação removida
        assert "5" not in processed  # Números removidos
        assert "desenvolvedor" in processed
        assert "python" in processed
    
    def test_preprocess_text_empty(self, mock_model_manager):
        """Testa pré-processamento com texto vazio"""
        assert mock_model_manager.preprocess_text("") == ""
        assert mock_model_manager.preprocess_text(None) == ""
        assert mock_model_manager.preprocess_text("   ") == ""
    
    def test_extract_candidate_text(self, mock_model_manager):
        """Testa extração de texto do candidato"""
        candidate = CandidateData(
            cv_pt="Desenvolvedor Python",
            cv_en="Python Developer",
            objetivo_profissional="Ser um bom dev",
            conhecimentos_tecnicos="Python, Django, FastAPI"
        )
        
        text = mock_model_manager.extract_candidate_text(candidate)
        
        # Verificações
        assert "desenvolvedor" in text
        assert "python" in text
        assert "django" in text
        assert len(text) > 0
    
    def test_extract_job_text(self, mock_model_manager):
        """Testa extração de texto da vaga"""
        job = JobData(
            titulo_vaga="Desenvolvedor Python Senior",
            objetivo_vaga="Desenvolver aplicações web",
            principais_atividades="Programar em Python",
            competencia_tecnicas_e_comportamentais="Python, Django, liderança"
        )
        
        text = mock_model_manager.extract_job_text(job)
        
        # Verificações
        assert "desenvolvedor" in text
        assert "python" in text
        assert "senior" in text
        assert len(text) > 0
    
    def test_generate_embedding(self, mock_model_manager):
        """Testa geração de embedding"""
        # Mock do sentence model
        mock_model_manager.sentence_model.encode.return_value = np.random.rand(1, 384)
        
        embedding = mock_model_manager.generate_embedding("test text")
        
        # Verificações
        assert isinstance(embedding, np.ndarray)
        assert embedding.shape == (384,)
        mock_model_manager.sentence_model.encode.assert_called_once()
    
    def test_generate_embedding_empty_text(self, mock_model_manager):
        """Testa geração de embedding com texto vazio"""
        mock_model_manager.sentence_model.encode.return_value = np.random.rand(1, 384)
        
        embedding = mock_model_manager.generate_embedding("")
        
        # Deve chamar com "texto vazio"
        mock_model_manager.sentence_model.encode.assert_called_with(["texto vazio"], device=mock_model_manager.device)
    
    def test_predict_match(self, mock_model_manager):
        """Testa predição de match"""
        # Mock do modelo neural
        mock_output = Mock()
        mock_output.cpu.return_value.numpy.return_value = np.array([[0.8]])
        mock_model_manager.neural_model.return_value = mock_output
        
        candidate_emb = np.random.rand(384)
        job_emb = np.random.rand(384)
        
        score = mock_model_manager.predict_match(candidate_emb, job_emb)
        
        # Verificações
        assert isinstance(score, float)
        assert 0 <= score <= 1
        mock_model_manager.neural_model.assert_called_once()
    
    def test_calculate_similarity(self, mock_model_manager):
        """Testa cálculo de similaridade"""
        emb1 = np.random.rand(384)
        emb2 = np.random.rand(384)
        
        similarity = mock_model_manager.calculate_similarity(emb1, emb2)
        
        # Verificações
        assert isinstance(similarity, float)
        assert -1 <= similarity <= 1

class TestAPI:
    """Testes para os endpoints da API"""
    
    @pytest.fixture
    def client(self):
        """Fixture para cliente de teste"""
        with patch('app.main.ModelManager'):
            return TestClient(app)
    
    @pytest.fixture
    def mock_model_manager_api(self):
        """Mock do model manager para testes de API"""
        with patch('app.main.model_manager') as mock_manager:
            # Configurar mocks
            mock_manager.extract_candidate_text.return_value = "desenvolvedor python"
            mock_manager.extract_job_text.return_value = "vaga python senior"
            mock_manager.generate_embedding.return_value = np.random.rand(384)
            mock_manager.calculate_similarity.return_value = 0.8
            mock_manager.predict_match.return_value = 0.85
            
            yield mock_manager
    
    def test_root_endpoint(self, client):
        """Testa endpoint raiz"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"
    
    def test_health_endpoint(self, client):
        """Testa endpoint de health check"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "models_loaded" in data
        assert data["models_loaded"] is True
    
    def test_predict_endpoint_success(self, client, mock_model_manager_api):
        """Testa endpoint de predição com sucesso"""
        request_data = {
            "candidate": {
                "cv_pt": "Desenvolvedor Python com 3 anos de experiência",
                "objetivo_profissional": "Trabalhar com desenvolvimento web"
            },
            "jobs": [
                {
                    "titulo_vaga": "Desenvolvedor Python Senior",
                    "objetivo_vaga": "Desenvolver aplicações web"
                }
            ],
            "top_k": 5,
            "threshold": 0.5
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verificar estrutura da resposta
        assert "candidate_processed_text" in data
        assert "recommendations" in data
        assert "processing_time_ms" in data
        assert "timestamp" in data
        
        # Verificar que o model manager foi chamado
        mock_model_manager_api.extract_candidate_text.assert_called_once()
        mock_model_manager_api.generate_embedding.assert_called()
    
    def test_predict_endpoint_empty_candidate(self, client, mock_model_manager_api):
        """Testa endpoint com candidato vazio"""
        # Mock para retornar texto vazio
        mock_model_manager_api.extract_candidate_text.return_value = ""
        
        request_data = {
            "candidate": {
                "cv_pt": "",
                "cv_en": ""
            },
            "jobs": [
                {
                    "titulo_vaga": "Desenvolvedor Python"
                }
            ]
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 400
        assert "insuficientes" in response.json()["detail"]
    
    def test_predict_endpoint_no_matches(self, client, mock_model_manager_api):
        """Testa endpoint sem matches acima do threshold"""
        # Mock para retornar score baixo
        mock_model_manager_api.predict_match.return_value = 0.2
        
        request_data = {
            "candidate": {
                "cv_pt": "Desenvolvedor Python"
            },
            "jobs": [
                {
                    "titulo_vaga": "Contador Senior"
                }
            ],
            "threshold": 0.8
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["recommendations"]) == 0
    
    def test_predict_endpoint_validation_error(self, client):
        """Testa erro de validação"""
        request_data = {
            "candidate": {
                "cv_pt": "Test"
            },
            "jobs": [],  # Lista vazia de jobs
            "top_k": 25,  # Acima do limite máximo
            "threshold": 1.5  # Acima do limite máximo
        }
        
        response = client.post("/predict", json=request_data)
        
        assert response.status_code == 422  # Validation error

class TestDataModels:
    """Testes para os modelos de dados Pydantic"""
    
    def test_candidate_data_model(self):
        """Testa modelo CandidateData"""
        candidate = CandidateData(
            cv_pt="Desenvolvedor Python",
            objetivo_profissional="Ser desenvolvedor senior"
        )
        
        assert candidate.cv_pt == "Desenvolvedor Python"
        assert candidate.cv_en == ""  # Valor padrão
        assert candidate.objetivo_profissional == "Ser desenvolvedor senior"
    
    def test_job_data_model(self):
        """Testa modelo JobData"""
        job = JobData(
            titulo_vaga="Desenvolvedor Python Senior",
            principais_atividades="Desenvolver aplicações"
        )
        
        assert job.titulo_vaga == "Desenvolvedor Python Senior"
        assert job.objetivo_vaga == ""  # Valor padrão
        assert job.principais_atividades == "Desenvolver aplicações"
    
    def test_prediction_request_validation(self):
        """Testa validação do request"""
        # Request válido
        request = PredictionRequest(
            candidate=CandidateData(cv_pt="Test"),
            jobs=[JobData(titulo_vaga="Test")]
        )
        
        assert request.top_k == 5  # Valor padrão
        assert request.threshold == 0.5  # Valor padrão
        
        # Testar limites
        with pytest.raises(ValueError):
            PredictionRequest(
                candidate=CandidateData(cv_pt="Test"),
                jobs=[JobData(titulo_vaga="Test")],
                top_k=0  # Abaixo do mínimo
            )
        
        with pytest.raises(ValueError):
            PredictionRequest(
                candidate=CandidateData(cv_pt="Test"),
                jobs=[JobData(titulo_vaga="Test")],
                threshold=-0.1  # Abaixo do mínimo
            )

class TestIntegration:
    """Testes de integração"""
    
    @pytest.mark.asyncio
    async def test_full_prediction_pipeline(self):
        """Testa pipeline completo de predição"""
        # Este teste simula o fluxo completo sem carregar modelos reais
        
        with patch('app.main.ModelManager') as MockManager:
            # Configurar mock
            mock_instance = MockManager.return_value
            mock_instance.extract_candidate_text.return_value = "desenvolvedor python"
            mock_instance.extract_job_text.return_value = "vaga python"
            mock_instance.generate_embedding.return_value = np.random.rand(384)
            mock_instance.calculate_similarity.return_value = 0.75
            mock_instance.predict_match.return_value = 0.8
            
            # Criar instância da API
            from app.main import app
            client = TestClient(app)
            
            # Fazer request
            request_data = {
                "candidate": {
                    "cv_pt": "Desenvolvedor Python com experiência em Django"
                },
                "jobs": [
                    {
                        "titulo_vaga": "Desenvolvedor Python Senior",
                        "principais_atividades": "Desenvolver APIs com Django"
                    }
                ]
            }
            
            response = client.post("/predict", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["recommendations"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app", "--cov-report=html"])