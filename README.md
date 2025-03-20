# RFM Insights - Análise RFM e Geração de Mensagens

## Descrição
RFM Insights é uma aplicação web para análise RFM (Recency, Frequency, Monetary) de clientes e geração de mensagens personalizadas. A aplicação permite que empresas analisem o comportamento de seus clientes e gerem mensagens personalizadas para diferentes segmentos.

## Estrutura do Projeto

```
rfm-insights/
├── app/                      # Frontend da aplicação
│   ├── assets/              # Recursos estáticos
│   │   ├── css/            # Arquivos CSS
│   │   └── js/             # Arquivos JavaScript
│   │       ├── api-client.js    # Cliente API
│   │       ├── config.js        # Configuração da aplicação
│   │       ├── state-manager.js # Gerenciador de estado
│   │       └── app.js           # Aplicação principal
│   ├── index.html          # Página principal
│   └── .env.example        # Exemplo de variáveis de ambiente
├── api/                     # Backend da aplicação
│   └── src/                # Código fonte do backend
│       ├── routes/         # Rotas da API
│       ├── controllers/    # Controladores
│       └── models/         # Modelos de dados
├── config/                 # Configurações do projeto
│   ├── config.py          # Configuração principal
│   ├── env_validator.py   # Validação de ambiente
│   ├── monitoring_config.py # Configuração de monitoramento
│   └── logging_config.py  # Configuração de logs
├── nginx/                  # Configuração do Nginx
│   └── nginx.conf         # Arquivo de configuração
├── docker-compose.yml     # Configuração do Docker Compose
├── Dockerfile.api         # Dockerfile para a API
├── install.sh            # Script de instalação
└── deploy.sh             # Script de deploy
```

## Configuração

### Variáveis de Ambiente
A aplicação utiliza variáveis de ambiente para configuração. Um arquivo `.env.example` está disponível como modelo:

```env
# Frontend Environment Variables
API_URL=https://api.rfminsights.com.br
API_VERSION=v1
API_TIMEOUT=30000

# Feature Flags
ENABLE_ANALYTICS=true
ENABLE_LOGGING=true

# Authentication
AUTH_DOMAIN=rfminsights.com.br
AUTH_ENDPOINT=/auth
AUTH_REDIRECT_URI=https://app.rfminsights.com.br/callback.html

# Application Settings
APP_NAME=RFM Insights
APP_VERSION=1.0.0
APP_ENV=production
```

### Sistema de Configuração
A aplicação utiliza um sistema de configuração centralizado através do arquivo `config.js`, que:
- Carrega variáveis de ambiente do arquivo `.env`
- Fornece valores padrão para configurações
- Está disponível globalmente como `window.appConfig`

## Arquitetura

### Frontend
- **API Client**: Gerencia todas as comunicações com o backend
- **State Manager**: Gerencia o estado global da aplicação
- **App**: Inicializa e coordena os componentes da aplicação

### Backend
- API RESTful construída com Python
- Estrutura modular com separação clara de responsabilidades
- Sistema de autenticação JWT

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/rfm-insights.git
cd rfm-insights
```

2. Copie o arquivo de exemplo de variáveis de ambiente:
```bash
cp app/.env.example app/.env
```

3. Execute o script de instalação:
```bash
./install.sh
```

## Desenvolvimento

Para iniciar o ambiente de desenvolvimento:

```bash
docker-compose up -d
```

A aplicação estará disponível em:
- Frontend: http://localhost:3000
- API: http://localhost:8000

## Deploy

Para fazer deploy da aplicação:

```bash
./deploy.sh
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Contato

Seu Nome - [@seu_twitter](https://twitter.com/seu_twitter) - email@exemplo.com

Link do Projeto: [https://github.com/seu-usuario/rfm-insights](https://github.com/seu-usuario/rfm-insights) 