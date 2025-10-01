# Deploy no Dokploy com Traefik - Guia Rápido

## O que foi alterado?

### 1. docker-compose.yml (Produção)
O arquivo principal agora está configurado para funcionar com Traefik/Dokploy:

✅ **Sem mapeamento de portas** - Usa `expose:` ao invés de `ports:` para evitar conflitos
✅ **Rede externa** - Conecta à rede `dokploy-network` do Traefik
✅ **Labels do Traefik** - Configurado para SSL automático e roteamento
✅ **Subpaths** - Prometheus em `/prometheus` e Grafana em `/grafana`
✅ **Container names** - Nomes únicos para facilitar gerenciamento

### 2. docker-compose.local.yml (Desenvolvimento)
Novo arquivo para desenvolvimento local que:

✅ **Mapeia portas** - 8000, 3000, 9090, 3100 para localhost
✅ **Rede local** - Usa bridge network `monitoring`
✅ **Configurações locais** - Grafana sem subpath, URLs locais

### 3. Domínio Configurado
Atualmente configurado para: **datathon.caiosaldanha.com**

Para usar seu próprio domínio, substitua em `docker-compose.yml`:
```yaml
# Buscar e substituir:
datathon.caiosaldanha.com → seu-dominio.com
```

## Como fazer deploy?

### Deploy em Produção (Dokploy/Traefik)

1. **Pré-requisitos:**
   - Traefik rodando na VPS
   - Rede `dokploy-network` criada
   - DNS apontando para a VPS

2. **Atualizar domínio:**
   ```bash
   # Editar docker-compose.yml e substituir datathon.caiosaldanha.com
   nano docker-compose.yml
   ```

3. **Deploy:**
   ```bash
   docker compose up -d --build
   ```

4. **Acessar:**
   - API: https://seu-dominio.com
   - Docs: https://seu-dominio.com/docs
   - Grafana: https://seu-dominio.com/grafana
   - Prometheus: https://seu-dominio.com/prometheus

### Deploy Local (Desenvolvimento)

1. **Usar script automático:**
   ```bash
   ./deploy.sh
   ```

2. **Ou manualmente:**
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.local.yml up -d --build
   ```

3. **Acessar:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3000
   - Prometheus: http://localhost:9090

## Resolução do Problema Original

**Erro anterior:**
```
Error: Bind for 0.0.0.0:3000 failed: port is already allocated
```

**Solução implementada:**
- Removido mapeamento de portas (`ports:`) do arquivo principal
- Adicionado `expose:` para comunicação interna
- Traefik agora gerencia todo o roteamento externo
- Portas não conflitam mais com outros serviços

## Arquivos Modificados

1. ✏️ `docker-compose.yml` - Configurado para Traefik/Dokploy
2. ➕ `docker-compose.local.yml` - Novo arquivo para desenvolvimento local
3. ✏️ `deploy.sh` - Atualizado para usar ambos os arquivos
4. ✏️ `README.md` - Documentação atualizada

## Comandos Úteis

```bash
# Ver logs
docker compose logs -f job-matching-api

# Parar serviços (produção)
docker compose down

# Parar serviços (local)
docker compose -f docker-compose.yml -f docker-compose.local.yml down

# Restart de um serviço
docker compose restart job-matching-api

# Ver status
docker compose ps
```

## Troubleshooting

### Erro: "network dokploy-network not found"
**Solução:** Certifique-se de que o Traefik está rodando e a rede existe:
```bash
docker network ls | grep dokploy
```

### Serviços não acessíveis via domínio
**Verificar:**
1. DNS está configurado corretamente?
2. Traefik está rodando?
3. Labels estão corretos no docker-compose.yml?
4. Firewall permite tráfego HTTP/HTTPS?

### Grafana não carrega dashboards
**Solução:**
```bash
# Verificar permissões
ls -la monitoring/grafana/

# Recriar volume se necessário
docker compose down
docker volume rm api-vagas_grafana_data
docker compose up -d
```

## Suporte

Para mais informações, consulte o README.md principal do projeto.
