# RFM Insights - Análise RFM e Geração de Mensagens

## Descrição
RFM Insights é uma aplicação web para análise RFM (Recency, Frequency, Monetary) de clientes e geração de mensagens personalizadas. A aplicação permite que empresas analisem o comportamento de seus clientes e gerem mensagens personalizadas para diferentes segmentos.

## Estrutura do Projeto
```
rfm-insights/
├── backend/                 # Aplicação backend
│   ├── __init__.py
│   ├── database.py         # Configuração do banco de dados
│   ├── models.py           # Modelos de banco de dados
│   ├── schemas.py          # Schemas Pydantic
│   └── security.py         # Utilitários de segurança
├── traefik/                # Configuração do Traefik
│   ├── traefik.yml         # Configuração principal
│   └── acme.json           # Armazenamento de certificados SSL
├── frontend/               # Arquivos estáticos do frontend
├── nginx/                  # Configuração do Nginx (apenas para o frontend)
│   └── nginx.conf          # Configuração do servidor
├── logs/                   # Logs da aplicação
├── analysis_history/       # Histórico de análises
├── pdfs/                   # Arquivos PDF gerados
├── requirements.txt        # Dependências Python
├── docker-compose.yml      # Configuração dos serviços Docker
├── Dockerfile.api          # Dockerfile da API
├── deploy.sh               # Script de deployment para Linux
├── .env.template           # Template para variáveis de ambiente
```

## Pré-requisitos

### Software Necessário
- Docker e Docker Compose
- Python 3.8+ (para desenvolvimento local)
- PostgreSQL 13+ (para desenvolvimento local)
- Chave de API OpenAI (para recursos de IA)

### Hardware Recomendado
- 4GB RAM mínimo (8GB recomendado)
- 10GB de espaço em disco

## Instalação e Deployment

### Configuração de Ambiente

1. **Clone o repositório**
```bash
git clone https://github.com/grsantoss/matriz-rfm.git
cd matriz-rfm
```

2. **Criar diretórios necessários**
```bash
# Linux/macOS
mkdir -p traefik frontend logs analysis_history pdfs

# Windows (PowerShell)
New-Item -ItemType Directory -Path traefik,frontend,logs,analysis_history,pdfs -Force
```

3. **Criar arquivo acme.json para certificados SSL**
```bash
# Linux/macOS
touch traefik/acme.json
chmod 600 traefik/acme.json

# Windows (PowerShell)
New-Item -ItemType File -Path traefik/acme.json -Force
# No Windows, não é possível definir permissões equivalentes a chmod 600
```

4. **Configurar variáveis de ambiente**
```bash
cp .env.template .env
# Edite o arquivo .env com suas configurações
```

### Deployment em Produção

#### Linux/Ubuntu
1. Configure seus domínios para apontar para o IP do servidor
2. Execute o script de deployment:
```bash
sudo bash deploy.sh
```

O script irá:
- Verificar todas as dependências
- Configurar o ambiente
- Verificar a configuração de DNS
- Iniciar todos os serviços com Docker Compose
- Verificar o deployment
- Exibir um resumo do deployment

#### Windows
1. Abra o PowerShell como Administrador
2. Navegue até o diretório do projeto
3. Execute:
```powershell
# Permitir a execução de scripts
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# Executar o script de deployment
./deploy.sh
```

### Verificação do Deployment

Após o deployment, verifique se:
1. Traefik está em execução e obteve certificados SSL
2. O frontend está acessível em https://app.rfminsights.com.br
3. A API está acessível em https://api.rfminsights.com.br
4. O painel do Traefik está acessível em https://traefik.rfminsights.com.br

## Configuração

### Variáveis de Ambiente Importantes

```
# Configuração do Banco de Dados
POSTGRES_USER=rfminsights
POSTGRES_PASSWORD=sua_senha_segura
POSTGRES_DB=rfminsights

# Configuração da API
JWT_SECRET_KEY=chave_secreta_muito_segura
OPENAI_API_KEY=sua_chave_api_openai
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=800
OPENAI_TEMPERATURE=0.7

# Configuração AWS (se necessário)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

### Configuração do OpenAI

1. Obtenha sua chave de API no [OpenAI Platform](https://platform.openai.com/)
2. Adicione a chave ao arquivo `.env` como `OPENAI_API_KEY=sua-chave-aqui`
3. Ajuste os parâmetros adicionais conforme necessário:
   - `OPENAI_MODEL`: gpt-4 (melhor qualidade) ou gpt-3.5-turbo (menor custo)
   - `OPENAI_MAX_TOKENS`: limite de tokens na resposta
   - `OPENAI_TEMPERATURE`: controla criatividade (0.0-1.0)

## Desenvolvimento Local

### Configuração do Ambiente de Desenvolvimento

1. **Criar e ativar ambiente virtual**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

2. **Instalar dependências**
```bash
pip install -r requirements.txt
```

3. **Configurar banco de dados local**
```bash
# Criar banco de dados PostgreSQL
createdb rfm_insights

# Atualizar arquivo .env com as credenciais do banco
```

4. **Executar migrações**
```bash
alembic upgrade head
```

5. **Iniciar o servidor de desenvolvimento**
```bash
uvicorn backend.main:app --reload
```

## Recursos da Aplicação

### Análise RFM

A aplicação utiliza análise RFM sofisticada para segmentar clientes nas seguintes categorias:

1. **Campeões**: Clientes recentes que compram frequentemente e gastam mais
2. **Clientes Leais**: Compram regularmente e gastam significativamente
3. **Potenciais Clientes Leais**: Clientes recentes com frequência média
4. **Novos Clientes**: Compraram recentemente, mas não frequentemente
5. **Clientes Promissores**: Clientes recentes com bom valor monetário
6. **Clientes que Precisam de Atenção**: Boa recência e frequência, mas baixo gasto
7. **Clientes em Risco**: Não compraram recentemente
8. **Clientes que Não Posso Perder**: Grandes compras, mas inativos recentemente
9. **Clientes Hibernando**: Abaixo da média em todas as métricas
10. **Clientes Perdidos**: Pontuações mais baixas em todas as métricas

### Recursos de IA

A aplicação utiliza a API do OpenAI para fornecer:

1. **Insights de Segmentos**:
   - Análise detalhada de cada segmento
   - Identificação de padrões comportamentais
   - Detecção de oportunidades
   - Avaliação de riscos
   - Recomendações estratégicas

2. **Sugestões de Marketing**:
   - Templates de email personalizados
   - Ideias de campanhas para cada segmento
   - Estratégias de engajamento acionáveis
   - Recomendações de conteúdo

3. **Geração Automatizada de Conteúdo**:
   - Mensagens de marketing específicas para segmentos
   - Templates de comunicação personalizados
   - Sugestões de copy para campanhas
   - Estratégias de engajamento

## Gerenciamento de Prompts

O sistema utiliza um gerenciamento centralizado de prompts localizado em `backend/utils/prompts.py`. Este arquivo contém todos os prompts de IA usados na aplicação.

### Categorias de Prompts

1. **Prompts de Sistema**:
   - Definem papéis da IA (analista, marketeiro, copywriter)
   - Estabelecem tom e nível de expertise
   - Configuram estilo de resposta

2. **Prompts de Análise de Segmento**:
   - Template de análise padrão
   - Templates específicos por segmento
   - Métricas e áreas de foco personalizáveis

3. **Prompts de Sugestão de Marketing**:
   - Template de marketing padrão
   - Templates específicos para campanhas
   - Formato de saída estruturado

4. **Prompts de Conteúdo para Marketplace**:
   - Descrições de produtos
   - Campanhas de email
   - Conteúdo para redes sociais

### Personalização de Prompts

Para modificar o comportamento ou saída da IA:

1. Abra `backend/utils/prompts.py`
2. Localize a categoria de prompt relevante
3. Edite ou adicione templates de prompt
4. Use variáveis de template: `{nome_variavel}`

## Manutenção

### Atualizações Regulares
```bash
# Atualizar dependências
pip install -r requirements.txt --upgrade

# Atualizar schema do banco de dados
alembic upgrade head

# Atualizar imagens Docker
docker-compose pull
```

### Backup
```bash
# Backup do banco de dados
pg_dump -U seu_usuario -d rfm_insights > backup.sql

# Backup das variáveis de ambiente
cp .env .env.backup
```

### Monitoramento
- Verificar logs no diretório `logs/`
- Monitorar uso da API
- Verificar espaço em disco regularmente

## Resolução de Problemas

### Banco de Dados
- **Erro de conexão**: Verifique credenciais no arquivo `.env`
- **Erro de migração**: Tente `alembic downgrade base` e depois `alembic upgrade head`

### Docker
- **Falha na inicialização**: Verifique logs com `docker-compose logs`
- **Problemas de rede**: Verifique configuração de rede do Docker e firewall

### Certificados SSL
- **Erro na obtenção de certificados**: Verifique se os domínios apontam para o IP correto
- **Certificados expirados**: O Traefik deve renovar automaticamente, verifique logs

## Suporte e Recursos

Para suporte, por favor:
1. Consulte a documentação
2. Revise os problemas comuns na seção de Resolução de Problemas
3. Abra uma issue no GitHub
4. Entre em contato: george@rtz.com.br

## Vantagens do Traefik sobre Nginx+Certbot

1. **Gerenciamento Automático de Certificados SSL**: O Traefik obtém e renova certificados automaticamente
2. **Configuração Simplificada**: Todo o roteamento é controlado via labels Docker
3. **Reconfiguração Dinâmica**: Serviços podem ser adicionados/removidos sem reiniciar o Traefik
4. **Monitoramento Aprimorado**: Painel integrado para monitorar rotas e serviços
5. **Melhor Integração com Docker**: Suporte nativo ao Docker com descoberta automática

## Comandos Úteis

```bash
# Visualizar logs
docker-compose logs

# Logs específicos de serviço
docker-compose logs [serviço]

# Reiniciar todos os serviços
docker-compose restart

# Parar todos os serviços
docker-compose down

# Atualizar e reimplantar
./deploy.sh
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

George Santos - [@grsantoss](https://twitter.com/grsantoss) - george@rtz.com.br

Link do Projeto: [https://github.com/grsantoss/matriz-rfm](https://github.com/grsantoss/matriz-rfm) 