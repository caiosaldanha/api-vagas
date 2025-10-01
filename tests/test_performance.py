"""
Testes de performance e carga para a API
"""
import pytest
import time
import concurrent.futures
from fastapi.testclient import TestClient
from unittest.mock import patch
import numpy as np

from app.main import app

class TestPerformance:
    """Testes de performance"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste com mock do model manager"""
        with patch('app.main.ModelManager') as MockManager:
            mock_instance = MockManager.return_value
            mock_instance.extract_candidate_text.return_value = "desenvolvedor python"
            mock_instance.extract_job_text.return_value = "vaga python"
            mock_instance.generate_embedding.return_value = np.random.rand(384)
            mock_instance.calculate_similarity.return_value = 0.75
            mock_instance.predict_match.return_value = 0.8
            
            return TestClient(app)
    
    def test_single_prediction_performance(self, client):
        """Testa performance de uma predição única"""
        request_data = {
            "candidate": {
                "cv_pt": "Desenvolvedor Python com 3 anos de experiência"
            },
            "jobs": [
                {
                    "titulo_vaga": f"Vaga {i}",
                    "objetivo_vaga": f"Objetivo da vaga {i}"
                }
                for i in range(10)  # 10 vagas
            ]
        }
        
        start_time = time.time()
        response = client.post("/predict", json=request_data)
        end_time = time.time()
        
        assert response.status_code == 200
        processing_time = (end_time - start_time) * 1000  # em ms
        
        # Deve processar em menos de 5 segundos (com mock)
        assert processing_time < 5000
    
    def test_multiple_jobs_scaling(self, client):
        """Testa escalabilidade com múltiplas vagas"""
        job_counts = [1, 10, 50, 100]
        times = []
        
        for count in job_counts:
            request_data = {
                "candidate": {
                    "cv_pt": "Desenvolvedor Python"
                },
                "jobs": [
                    {
                        "titulo_vaga": f"Vaga {i}",
                        "objetivo_vaga": f"Objetivo {i}"
                    }
                    for i in range(count)
                ]
            }
            
            start_time = time.time()
            response = client.post("/predict", json=request_data)
            end_time = time.time()
            
            assert response.status_code == 200
            times.append(end_time - start_time)
        
        # Verificar que o tempo cresce de forma aproximadamente linear
        # (com mock, deve ser muito rápido)
        for t in times:
            assert t < 10  # Menos de 10 segundos com mock
    
    def test_concurrent_requests(self, client):
        """Testa requisições concorrentes"""
        request_data = {
            "candidate": {
                "cv_pt": "Desenvolvedor Python"
            },
            "jobs": [
                {
                    "titulo_vaga": "Desenvolvedor Senior",
                    "objetivo_vaga": "Desenvolver aplicações"
                }
            ]
        }
        
        def make_request():
            response = client.post("/predict", json=request_data)
            return response.status_code
        
        # Fazer 5 requisições concorrentes
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]
        
        # Todas devem ter sucesso
        assert all(status == 200 for status in results)

class TestEdgeCases:
    """Testes de casos extremos"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste"""
        with patch('app.main.ModelManager') as MockManager:
            mock_instance = MockManager.return_value
            mock_instance.extract_candidate_text.return_value = "texto processado"
            mock_instance.extract_job_text.return_value = "vaga processada"
            mock_instance.generate_embedding.return_value = np.random.rand(384)
            mock_instance.calculate_similarity.return_value = 0.5
            mock_instance.predict_match.return_value = 0.6
            
            return TestClient(app)
    
    def test_very_long_text(self, client):
        """Testa com texto muito longo"""
        long_text = "Python " * 1000  # Texto muito longo
        
        request_data = {
            "candidate": {
                "cv_pt": long_text
            },
            "jobs": [
                {
                    "titulo_vaga": "Desenvolvedor",
                    "objetivo_vaga": long_text
                }
            ]
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 200
    
    def test_special_characters(self, client):
        """Testa com caracteres especiais"""
        text_with_special = "Programador C++ & C# com experiência em .NET, Node.js e Vue.js! @dev #python"
        
        request_data = {
            "candidate": {
                "cv_pt": text_with_special
            },
            "jobs": [
                {
                    "titulo_vaga": text_with_special
                }
            ]
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 200
    
    def test_unicode_characters(self, client):
        """Testa com caracteres unicode"""
        unicode_text = "Desenvolvedor com experiência em aplicações móveis 📱 e web 🌐"
        
        request_data = {
            "candidate": {
                "cv_pt": unicode_text
            },
            "jobs": [
                {
                    "titulo_vaga": unicode_text
                }
            ]
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 200
    
    def test_minimum_threshold(self, client):
        """Testa com threshold mínimo"""
        request_data = {
            "candidate": {
                "cv_pt": "Desenvolvedor"
            },
            "jobs": [
                {
                    "titulo_vaga": "Vaga"
                }
            ],
            "threshold": 0.0
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 200
    
    def test_maximum_threshold(self, client):
        """Testa com threshold máximo"""
        request_data = {
            "candidate": {
                "cv_pt": "Desenvolvedor"
            },
            "jobs": [
                {
                    "titulo_vaga": "Vaga"
                }
            ],
            "threshold": 1.0
        }
        
        response = client.post("/predict", json=request_data)
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])