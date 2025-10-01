# Job Matching API - Deep Learning & NLP

Um sistema completo de matching de vagas utilizando Deep Learning e Processamento de Linguagem Natural (NLP) para conectar candidatos às oportunidades mais adequadas ao seu perfil.

## 📋 Visão Geral do Projeto

### Objetivo
Este projeto resolve o problema de negócio de **matching inteligente entre candidatos e vagas de emprego**, utilizando técnicas avançadas de Machine Learning para analisar CVs, descrições de vagas e gerar recomendações precisas baseadas em similaridade semântica.

### Solução Proposta
Construção de uma pipeline completa de machine learning que inclui:
- Pré-processamento de texto e extração de features
- Geração de embeddings semânticos com Sentence Transformers
- Rede neural personalizada para scoring de compatibilidade
- API REST para predições em tempo real
- Sistema de monitoramento contínuo com detecção de drift


## 🛠️ Stack Tecnológica

- **Linguagem**: Python 3.10+
- **Frameworks de ML**: 
  - PyTorch (apenas inferência, versão 2.0.1, compatível com CPU)
  - Sentence Transformers (embeddings semânticos, CPU)
  - scikit-learn (métricas e pré-processamento)
- **API**: FastAPI com validação Pydantic
- **Serialização**: joblib e PyTorch (.pth)
- **Testes**: pytest (apenas para desenvolvimento)
- **Empacotamento**: Docker & Docker Compose
- **Deploy**: Cloud VPS ou máquina enxuta (sem GPU)

- **Monitoramento**: 
  - Prometheus (métricas)
  - Grafana (dashboards)
  - Loki (agregação de logs)

## ⚠️ Arquivos Grandes

Alguns arquivos de dados e modelos excedem o limite de 100MB do GitHub e não estão presentes no repositório. Para utilizar o sistema completo, faça o download dos arquivos grandes diretamente na seção de [Releases](https://github.com/caiosaldanha/api-vagas/releases) do GitHub.

- `model/candidate_texts_processed.joblib`
- `data-files/applicants.json`
- Outros arquivos grandes, se necessário

Após baixar, coloque-os nas respectivas pastas do projeto.

## 📁 Estrutura do Projeto

```
api-vagas/
├── app/
│   ├── __init__.py
│   └── main.py                    # API FastAPI principal
├── tests/
│   ├── __init__.py
│   ├── test_main.py              # Testes unitários principais
│   └── test_performance.py       # Testes de performance
├── model/
│   ├── candidate_embeddings.npy          # Embeddings pré-computados
│   ├── job_embeddings.npy               # Embeddings das vagas
│   ├── job_matching_neural_model.pth    # Modelo neural treinado
│   ├── candidate_texts_processed.joblib # Textos processados
│   └── job_texts_processed.joblib       # Textos de vagas processados
├── data-files/
│   ├── applicants.json          # Dados dos candidatos (195MB)
│   ├── prospects.json           # Prospects (21MB)
│   └── vagas.json              # Vagas disponíveis (37MB)
├── monitoring/
│   ├── prometheus.yml           # Configuração Prometheus
│   ├── loki-config.yml         # Configuração Loki
│   ├── promtail-config.yml     # Configuração Promtail
│   └── grafana/
│       ├── datasources/        # Fontes de dados Grafana
│       └── dashboards/         # Dashboards pré-configurados
├── logs/                       # Diretório de logs
├── requirements.txt            # Dependências Python
├── Dockerfile                  # Container da aplicação
├── docker-compose.yml         # Orquestração completa
├── pytest.ini                # Configuração de testes
├── model_nlp_deep_learning.ipynb  # Notebook de desenvolvimento
└── README.md                  # Este arquivo
```

## 🚀 Instruções de Deploy


### Pré-requisitos
- Docker & Docker Compose
- Python 3.10+ (para desenvolvimento local)
- 4GB+ RAM (suficiente para inferência)
- **Não requer GPU**


### 1. Deploy Completo com Docker Compose (Desenvolvimento Local)

Para desenvolvimento local, use o arquivo de override que mapeia portas:

```bash
# Clone ou acesse o diretório do projeto
cd api-vagas

# Opção 1: Usar o script de deploy (recomendado para local)
./deploy.sh

# Opção 2: Comando manual
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build -d

# Verificar status dos containers
docker compose ps

# Visualizar logs em tempo real
docker compose logs -f job-matching-api

# Parar todos os serviços
docker compose -f docker-compose.yml -f docker-compose.local.yml down
```

### 2. Acessar Serviços (Deploy Local)

- **API**: http://localhost:8000
- **Documentação Swagger**: http://localhost:8000/docs
- **Grafana Dashboard**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Health Check**: http://localhost:8000/health

### 3. Deploy em VPS com Traefik (Dokploy)

Este projeto está configurado para deploy em VPS com Traefik reverse proxy (ex: Dokploy).

**Características do deploy em produção:**
- Usa `expose` ao invés de `ports` para evitar conflitos de porta
- Configurado para funcionar com Traefik como reverse proxy
- SSL/TLS automático via Let's Encrypt
- Subpaths configurados para Prometheus (`/prometheus`) e Grafana (`/grafana`)
- Rede externa `dokploy-network` para comunicação com Traefik

**Acessar Serviços (Produção - exemplo com datathon.caiosaldanha.com):**
- **API**: https://datathon.caiosaldanha.com
- **Documentação Swagger**: https://datathon.caiosaldanha.com/docs
- **Grafana Dashboard**: https://datathon.caiosaldanha.com/grafana (admin/admin123)
- **Prometheus**: https://datathon.caiosaldanha.com/prometheus
- **Health Check**: https://datathon.caiosaldanha.com/health

**Configuração:**
1. Certifique-se de que o Traefik está rodando e a rede `dokploy-network` existe
2. Atualize o domínio nos labels do `docker-compose.yml` para seu domínio
3. Deploy com: `docker compose up -d --build`

**Nota:** Loki e Promtail são internos e não têm acesso externo (apenas usado pelo Grafana).

### 4. Deploy Local para Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Executar testes
pytest tests/ -v --cov=app --cov-report=html

# Ver relatório de cobertura
open htmlcov/index.html
```

### 5. Comandos Úteis

```bash
# Parar todos os serviços
docker-compose down

# Rebuild apenas a API
docker-compose up --build job-matching-api

# Ver métricas Prometheus
curl http://localhost:8000/metrics

# Logs específicos
docker-compose logs grafana
docker-compose logs prometheus
```

## 📊 Exemplos de Chamadas à API

### 1. Health Check

```bash
curl -X GET "http://localhost:8000/health" \
     -H "Content-Type: application/json"
```

**Resposta:**
```json
{
  "status": "healthy",
  "device": "cpu",
  "models_loaded": true,
  "timestamp": "2023-12-01T10:30:00"
}
```

### 2. Predição de Matches - Exemplo Básico

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "candidate": {
         "cv_pt": "Desenvolvedor Python com 3 anos de experiência em Django e FastAPI. Formação em Ciência da Computação.",
         "objetivo_profissional": "Trabalhar com desenvolvimento de APIs e sistemas web escaláveis"
       },
       "jobs": [
         {
           "titulo_vaga": "Desenvolvedor Python Senior",
           "objetivo_vaga": "Desenvolver APIs REST com Python",
           "principais_atividades": "Programação em Python, Django, FastAPI, PostgreSQL",
           "competencia_tecnicas_e_comportamentais": "Python, Django, FastAPI, SQL, Git, trabalho em equipe"
         },
         {
           "titulo_vaga": "Analista de Marketing Digital",
           "objetivo_vaga": "Gerenciar campanhas de marketing digital",
           "principais_atividades": "Google Ads, Facebook Ads, análise de dados",
           "competencia_tecnicas_e_comportamentais": "Marketing digital, Google Analytics, criatividade"
         }
       ],
       "top_k": 5,
       "threshold": 0.3
     }'
```

**Resposta:**
```json
{
  "candidate_processed_text": "desenvolvedor python anos experiencia django fastapi formacao ciencia computacao trabalhar desenvolvimento apis sistemas web escalaveis",
  "recommendations": [
    {
      "job_index": 0,
      "similarity_score": 0.8542,
      "ml_score": 0.9156,
      "job_preview": "desenvolvedor python senior desenvolver apis rest python programacao python django fastapi postgresql python django fastapi sql git trabalho equipe..."
    }
  ],
  "processing_time_ms": 245.8,
  "timestamp": "2023-12-01T10:35:22.123456"
}
```

### 3. Exemplo com Script Python

```python
import requests
import json

# Dados do candidato
candidate_data = {
    "candidate": {
        "cv_pt": "Engenheiro de Machine Learning com experiência em PyTorch, TensorFlow e MLOps",
        "conhecimentos_tecnicos": "Python, PyTorch, TensorFlow, Docker, Kubernetes, AWS"
    },
    "jobs": [
        {
            "titulo_vaga": "ML Engineer",
            "principais_atividades": "Desenvolver modelos de ML em produção",
            "competencia_tecnicas_e_comportamentais": "Python, PyTorch, MLOps, Docker"
        }
    ],
    "top_k": 3,
    "threshold": 0.5
}

# Fazer requisição
response = requests.post(
    "http://localhost:8000/predict",
    json=candidate_data,
    headers={"Content-Type": "application/json"}
)

# Processar resposta
if response.status_code == 200:
    result = response.json()
    print(f"Encontrados {len(result['recommendations'])} matches")
    for i, match in enumerate(result['recommendations'], 1):
        print(f"{i}. Job {match['job_index']} - Score: {match['ml_score']:.3f}")
else:
    print(f"Erro: {response.status_code} - {response.text}")
```


## 🔬 Pipeline de Machine Learning

### Etapas do Pipeline (API)

1. **Extração de Dados Textuais**
  - Utiliza arquivos serializados da pasta `model` (embeddings e textos processados)
  - Não realiza treinamento, apenas predição

2. **Pré-processamento de Texto**
  - Conversão para minúsculas
  - Remoção de pontuação e números
  - Remoção de stopwords em português
  - Normalização de espaços

3. **Engenharia de Features**
  - Geração de embeddings semânticos com Sentence Transformers (all-MiniLM-L6-v2, CPU)
  - Vetores de 384 dimensões

4. **Predição**
  - Rede neural carregada via arquivo `.pth` (apenas inferência)
  - Similaridade coseno + score da rede neural
  - Threshold configurável para filtragem
  - Ranking por score do modelo neural

5. **Pós-processamento**
  - Ordenação por score decrescente
  - Limitação aos top-k resultados
  - Aplicação de threshold de confiança

*Nota: Métricas do modelo são referentes ao treinamento realizado previamente, não pela API.*

## 📈 Monitoramento e Observabilidade

### Métricas Disponíveis

- **Requisições por minuto**: Volume de predições
- **Tempo de processamento**: Latência da API
- **Score ML médio**: Qualidade das predições
- **Taxa de matches**: Efetividade do modelo
- **Taxa de erro**: Confiabilidade do sistema

### Dashboards Grafana

1. **Overview Geral**: Métricas principais em tempo real
2. **Model Drift**: Monitoramento de performance do modelo
3. **API Performance**: Latência e throughput
4. **Logs Estruturados**: Análise de comportamento

### Alertas Configuráveis

- Taxa de erro > 5%
- Tempo de processamento > 10s
- Queda na taxa de matches
- Drift significativo no score médio

## 🧪 Testes e Qualidade

### Cobertura de Testes: 80%+

```bash
# Executar todos os testes
pytest tests/ -v

# Testes com cobertura
pytest tests/ --cov=app --cov-report=html

# Apenas testes de performance
pytest tests/test_performance.py -v

# Testes com marcadores
pytest -m "not slow" -v
```

### Tipos de Teste

- **Unitários**: Funções individuais e classes
- **Integração**: Pipeline completo de predição
- **Performance**: Carga e escalabilidade
- **API**: Endpoints e validação de dados

## 🔧 Configuração e Customização

### Variáveis de Ambiente

```bash
# Docker Compose
GRAFANA_ADMIN_PASSWORD=admin123
PROMETHEUS_RETENTION=200h

# API
PYTHONPATH=/app
MODEL_DIR=/app/model
LOG_LEVEL=INFO
```

### Ajuste de Hiperparâmetros

Editar `app/main.py`:

```python
# Threshold padrão para matches
DEFAULT_THRESHOLD = 0.5

# Top-K padrão
DEFAULT_TOP_K = 5

# Configuração da rede neural
EMBEDDING_DIM = 384
HIDDEN_DIM = 256
```

## 📚 Próximos Passos

- [ ] Implementar re-treinamento automático
- [ ] Adicionar suporte a múltiplos idiomas
- [ ] Integração com sistemas de RH
- [ ] Explicabilidade das recomendações
- [ ] API para feedback e aprendizado contínuo
- [ ] Deploy em Kubernetes
- [ ] Cache Redis para embeddings
- [ ] Versionamento de modelos com MLflow

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Commit: `git commit -m 'Adiciona nova feature'`
4. Push: `git push origin feature/nova-feature`
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas e suporte:
- Abra uma issue no repositório
- Consulte a documentação Swagger em `/docs`
- Verifique os logs em tempo real com `docker-compose logs -f`

---

**Desenvolvido com ❤️ usando Python, PyTorch e FastAPI**