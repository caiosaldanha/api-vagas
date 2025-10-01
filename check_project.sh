#!/bin/bash

# Verificar estrutura do projeto
echo "🔍 Verificando estrutura do projeto Job Matching API..."
echo ""

# Verificar se todos os arquivos estão presentes
FILES=(
    "app/main.py"
    "tests/test_main.py"
    "tests/test_performance.py"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    "README.md"
    "deploy.sh"
    "test_api.py"
    "pytest.ini"
    ".gitignore"
    "monitoring/prometheus.yml"
    "monitoring/grafana/dashboards/job-matching-dashboard.json"
)

echo "📁 Verificando arquivos essenciais:"
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - FALTANDO"
    fi
done

echo ""
echo "📁 Verificando diretórios:"

DIRS=(
    "app"
    "tests" 
    "model"
    "data-files"
    "monitoring"
    "monitoring/grafana"
    "monitoring/grafana/dashboards"
    "monitoring/grafana/datasources"
)

for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ - FALTANDO"
    fi
done

echo ""
echo "📊 Estatísticas do projeto:"
echo "   Linhas de código (Python): $(find . -name "*.py" -exec wc -l {} + | tail -1 | awk '{print $1}')"
echo "   Arquivos Python: $(find . -name "*.py" | wc -l)"
echo "   Arquivos de configuração: $(find . -name "*.yml" -o -name "*.yaml" -o -name "*.json" | wc -l)"
echo "   Tamanho total: $(du -sh . | cut -f1)"

echo ""
echo "🚀 Para iniciar o projeto:"
echo "   1. ./deploy.sh"
echo "   2. python3 test_api.py"
echo ""
echo "📖 Documentação completa no README.md"