#!/bin/bash

# Script de deploy automatizado para Job Matching API
# NOTA: Este script é para deploy LOCAL com portas mapeadas.
# Para deploy em produção com Traefik/Dokploy, use: docker compose up -d --build

set -e

echo "🚀 Iniciando deploy do Job Matching API..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs
mkdir -p prometheus_data
mkdir -p grafana_data

# Definir permissões para Grafana
echo "🔐 Configurando permissões..."
sudo chown -R 472:472 grafana_data/ || echo "⚠️ Não foi possível alterar permissões do Grafana (pode precisar de sudo)"

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker compose -f docker-compose.yml -f docker-compose.local.yml down || echo "Nenhum container rodando"

# Construir e iniciar serviços
echo "🔨 Construindo e iniciando serviços..."
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verificar status dos serviços
echo "✅ Verificando status dos serviços..."
docker-compose ps

# Testar endpoints
echo "🧪 Testando endpoints..."

# Health check da API
echo "Testing API health..."
curl -f http://localhost:8000/health || echo "⚠️ API health check falhou"

# Verificar Grafana
echo "Testing Grafana..."
curl -f http://localhost:3000 || echo "⚠️ Grafana não está respondendo"

# Verificar Prometheus
echo "Testing Prometheus..."
curl -f http://localhost:9090 || echo "⚠️ Prometheus não está respondendo"

echo ""
echo "🎉 Deploy concluído!"
echo ""
echo "📊 Serviços disponíveis:"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
echo "   Grafana: http://localhost:3000 (admin/admin123)"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "📋 Comandos úteis:"
echo "   Logs da API: docker compose logs -f job-matching-api"
echo "   Parar tudo: docker compose -f docker-compose.yml -f docker-compose.local.yml down"
echo "   Restart: docker compose restart"
echo ""
echo "🚀 Sistema pronto para uso!"