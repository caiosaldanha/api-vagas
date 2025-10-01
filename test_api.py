#!/usr/bin/env python3
"""
Script de exemplo para testar a API de Job Matching
"""

import requests
import json
import time
from typing import Dict, List

class JobMatchingAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    def health_check(self) -> Dict:
        """Verificar saúde da API"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def predict_matches(self, candidate: Dict, jobs: List[Dict], 
                       top_k: int = 5, threshold: float = 0.5) -> Dict:
        """Predizer matches entre candidato e vagas"""
        payload = {
            "candidate": candidate,
            "jobs": jobs,
            "top_k": top_k,
            "threshold": threshold
        }
        
        response = requests.post(
            f"{self.base_url}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()

def main():
    # Inicializar cliente
    client = JobMatchingAPIClient()
    
    print("🧪 Testando Job Matching API...\n")
    
    # 1. Health Check
    print("1. Health Check")
    try:
        health = client.health_check()
        print(f"✅ Status: {health['status']}")
        print(f"   Device: {health['device']}")
        print(f"   Models: {'✅' if health['models_loaded'] else '❌'}")
    except Exception as e:
        print(f"❌ Health check falhou: {e}")
        return
    
    print("\n" + "="*50 + "\n")
    
    # 2. Exemplo de Predição - Desenvolvedor Python
    print("2. Teste: Desenvolvedor Python")
    
    candidate_dev = {
        "cv_pt": "Desenvolvedor Python com 5 anos de experiência em Django, FastAPI e PostgreSQL. Experiência com Docker, Git e metodologias ágeis.",
        "objetivo_profissional": "Trabalhar como desenvolvedor backend senior em projetos desafiadores",
        "conhecimentos_tecnicos": "Python, Django, FastAPI, PostgreSQL, Docker, Git, REST APIs, pytest"
    }
    
    jobs_tech = [
        {
            "titulo_vaga": "Desenvolvedor Python Senior",
            "objetivo_vaga": "Desenvolver APIs e sistemas backend escaláveis",
            "principais_atividades": "Programação em Python, desenvolvimento de APIs REST, trabalho com bancos de dados PostgreSQL",
            "competencia_tecnicas_e_comportamentais": "Python, Django, FastAPI, PostgreSQL, Docker, trabalho em equipe, proatividade"
        },
        {
            "titulo_vaga": "Analista de Marketing Digital",
            "objetivo_vaga": "Gerenciar campanhas de marketing digital e análise de dados",
            "principais_atividades": "Google Ads, Facebook Ads, análise de métricas, criação de conteúdo",
            "competencia_tecnicas_e_comportamentais": "Marketing digital, Google Analytics, criatividade, comunicação"
        },
        {
            "titulo_vaga": "DevOps Engineer",
            "objetivo_vaga": "Automatizar deploy e infraestrutura",
            "principais_atividades": "Docker, Kubernetes, CI/CD, monitoramento de aplicações",
            "competencia_tecnicas_e_comportamentais": "Docker, Kubernetes, AWS, Python, shell script, proatividade"
        }
    ]
    
    try:
        start_time = time.time()
        result_dev = client.predict_matches(candidate_dev, jobs_tech, top_k=3, threshold=0.3)
        end_time = time.time()
        
        print(f"⏱️ Tempo de processamento: {end_time - start_time:.2f}s")
        print(f"📊 Processamento interno: {result_dev['processing_time_ms']:.1f}ms")
        print(f"🎯 Matches encontrados: {len(result_dev['recommendations'])}")
        
        print("\n📋 Resultados:")
        for i, match in enumerate(result_dev['recommendations'], 1):
            print(f"   {i}. Job {match['job_index']} - ML Score: {match['ml_score']:.3f} - Similarity: {match['similarity_score']:.3f}")
            print(f"      Preview: {match['job_preview'][:100]}...")
            print()
        
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
    
    print("="*50 + "\n")
    
    # 3. Exemplo - Data Scientist
    print("3. Teste: Data Scientist")
    
    candidate_ds = {
        "cv_pt": "Cientista de dados com mestrado em estatística. Experiência com Python, R, machine learning e deep learning.",
        "conhecimentos_tecnicos": "Python, R, pandas, scikit-learn, TensorFlow, PyTorch, SQL, estatística, machine learning"
    }
    
    jobs_ds = [
        {
            "titulo_vaga": "Data Scientist Senior",
            "principais_atividades": "Desenvolver modelos de machine learning, análise de dados, Python, R",
            "competencia_tecnicas_e_comportamentais": "Python, R, machine learning, estatística, SQL, comunicação"
        },
        {
            "titulo_vaga": "Vendedor Externo",
            "principais_atividades": "Vendas porta a porta, relacionamento com clientes",
            "competencia_tecnicas_e_comportamentais": "Comunicação, persuasão, proatividade"
        }
    ]
    
    try:
        result_ds = client.predict_matches(candidate_ds, jobs_ds, top_k=2, threshold=0.4)
        
        print(f"🎯 Matches encontrados: {len(result_ds['recommendations'])}")
        
        for i, match in enumerate(result_ds['recommendations'], 1):
            print(f"   {i}. Job {match['job_index']} - ML Score: {match['ml_score']:.3f}")
        
    except Exception as e:
        print(f"❌ Erro na predição: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # 4. Teste de Performance
    print("4. Teste de Performance (múltiplas vagas)")
    
    # Criar 20 vagas similares
    many_jobs = []
    for i in range(20):
        many_jobs.append({
            "titulo_vaga": f"Desenvolvedor {i}",
            "objetivo_vaga": f"Desenvolver software {i}",
            "principais_atividades": f"Programação, desenvolvimento {i}",
            "competencia_tecnicas_e_comportamentais": f"Python, programação {i}"
        })
    
    try:
        start_time = time.time()
        result_perf = client.predict_matches(candidate_dev, many_jobs, top_k=5, threshold=0.2)
        end_time = time.time()
        
        print(f"⏱️ Tempo total: {end_time - start_time:.2f}s para {len(many_jobs)} vagas")
        print(f"📊 Processamento interno: {result_perf['processing_time_ms']:.1f}ms")
        print(f"🎯 Matches encontrados: {len(result_perf['recommendations'])}")
        
    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
    
    print("\n✅ Testes concluídos!")
    print("\n📊 Para monitoramento:")
    print("   Grafana: http://localhost:3000")
    print("   Prometheus: http://localhost:9090")
    print("   Métricas API: http://localhost:8000/metrics")

if __name__ == "__main__":
    main()