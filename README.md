# RFM Insights - Análise RFM e Geração de Mensagens

## Descrição
RFM Insights é uma aplicação web para análise RFM (Recency, Frequency, Monetary) de clientes e geração de mensagens personalizadas. A aplicação permite que empresas analisem o comportamento de seus clientes e gerem mensagens personalizadas para diferentes segmentos.

## Project Structure
```
rfm-insights/
├── backend/                 # Backend application
│   ├── __init__.py
│   ├── database.py         # Database configuration
│   ├── models.py           # Database models
│   ├── schemas.py          # Pydantic schemas
│   └── security.py         # Security utilities
├── alembic/                # Database migrations
│   ├── versions/          # Migration versions
│   ├── env.py             # Alembic environment
│   └── script.py.mako     # Migration template
├── frontend/              # Frontend static files
│   ├── static/           # Static assets
│   └── templates/        # HTML templates
├── nginx/                 # Nginx configuration
│   └── nginx.conf        # Server config
├── alembic.ini           # Alembic configuration
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Docker services config
├── Dockerfile.api        # API Dockerfile
├── deploy.sh            # Linux deployment script
├── deploy-windows.ps1   # Windows deployment script
├── verify-deployment.ps1 # Deployment verification
└── .env.template        # Environment variables template
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

## Installation Guide

### Prerequisites Installation

#### Installing Python (3.8+)
```bash
# Windows
# Download from https://www.python.org/downloads/
# Or use winget
winget install Python.Python.3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify installation
python --version  # or python3 --version on Linux
```

#### Installing Docker & Docker Compose
```bash
# Windows
# Download Docker Desktop from https://www.docker.com/products/docker-desktop/
# Or use winget
winget install Docker.DockerDesktop

# Ubuntu/Debian
sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt update
sudo apt install docker-ce docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### Installing PostgreSQL
```bash
# Windows
# Download from https://www.postgresql.org/download/windows/
# Or use winget
winget install PostgreSQL.PostgreSQL

# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Verify installation
psql --version

# Create database
# Windows
createdb -U postgres rfm_insights

# Linux
sudo -u postgres createdb rfm_insights
```

#### Setting up OpenAI API Key
1. Create an account at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to API keys section
3. Create a new secret key
4. Add the key to your `.env` file as `OPENAI_API_KEY=your-key-here`

### Quick Start Guide

#### Prerequisites
Before installation, ensure you have:
1. Python 3.8 or higher
2. Docker Desktop for Windows (or Docker + Docker Compose for Linux)
3. PostgreSQL 13 or higher
4. OpenAI API key
5. 4GB RAM minimum (8GB recommended)
6. 10GB free disk space

### One-Click Installation

#### Windows
1. Open PowerShell as Administrator
2. Navigate to the project directory
3. Run:
```powershell
.\deploy-windows.ps1
```

#### Linux/Ubuntu
1. Open terminal
2. Navigate to the project directory
3. Run:
```bash
sudo bash deploy.sh
```

The deployment script will:
- Verify all prerequisites
- Create necessary directories
- Set up environment variables
- Install dependencies
- Initialize the database
- Start all services
- Verify the deployment

### Manual Installation Steps
If you prefer to install manually or the automatic script fails:

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/rfm-insights.git
cd rfm-insights
```

2. **Set up environment variables**
```bash
cp .env.template .env
# Edit .env with your settings
```

3. **Install Python dependencies**
```bash
# Create and activate virtual environment (recommended)
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

4. **Initialize the database**
```bash
# Create database if not exists
# Windows
createdb -U postgres rfm_insights
# Linux
sudo -u postgres createdb rfm_insights

# Run migrations
alembic upgrade head
```

5. **Start the services**
```bash
# Windows
docker-compose -f docker-compose-windows.yml up -d

# Linux
docker-compose up -d
```

6. **Create admin user (if not created automatically)**
```bash
# Run the following Python script
python -c "from backend.security import create_admin_user; create_admin_user()"
```

### Verification
After installation, verify the deployment:
```bash
# Windows
python scripts/verify_prerequisites.py

# Linux
python3 scripts/verify_prerequisites.py
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Database Connection Issues
1. **Error**: "Could not connect to database"
   - Check PostgreSQL is running:
     ```bash
     # Windows
     net start postgresql
     # Linux
     sudo systemctl status postgresql
     ```
   - Verify database credentials in .env
   - Ensure database exists:
     ```bash
     # Windows
     createdb -U postgres rfm_insights
     # Linux
     sudo -u postgres createdb rfm_insights
     ```
   - Check port 5432 is not blocked:
     ```bash
     # Windows
     netstat -an | findstr 5432
     # Linux
     netstat -an | grep 5432
     ```

2. **Error**: "Alembic migration failed"
   - Reset migrations:
     ```bash
     alembic downgrade base
     ```
   - Recreate migrations:
     ```bash
     alembic revision --autogenerate -m "reset"
     ```
   - Apply migrations:
     ```bash
     alembic upgrade head
     ```

#### Docker Issues
1. **Error**: "Docker daemon not running"
   - Start Docker Desktop (Windows)
   - Run:
     ```bash
     # Linux
     sudo systemctl start docker
     ```

2. **Error**: "Port already in use"
   - Check running containers:
     ```bash
     docker ps
     ```
   - Stop conflicting services:
     ```bash
     # Example to stop service using port 80
     # Windows
     netstat -ano | findstr :80
     taskkill /PID [PID] /F
     # Linux
     sudo lsof -i :80
     sudo kill -9 [PID]
     ```
   - Change ports in docker-compose.yml

#### OpenAI Integration Issues
1. **Error**: "Invalid API key"
   - Verify API key in .env
   - Check OpenAI account status:
     ```bash
     curl -s https://api.openai.com/v1/models \
       -H "Authorization: Bearer $OPENAI_API_KEY" | jq
     ```
   - Ensure sufficient API credits

2. **Error**: "API rate limit exceeded"
   - Implement request throttling
   - Check usage limits
   - Consider upgrading API plan

### Security Best Practices

1. **Environment Variables**
   - Never commit .env file
   - Use strong passwords
   - Rotate API keys regularly

2. **Database Security**
   - Use strong passwords
   - Enable SSL connections:
     ```bash
     # In postgresql.conf
     ssl = on
     ```
   - Regular backups:
     ```bash
     # Windows
     pg_dump -U postgres rfm_insights > backup.sql
     # Linux
     sudo -u postgres pg_dump rfm_insights > backup.sql
     ```
   - Limit database access

3. **Application Security**
   - Change default admin password
   - Enable HTTPS
   - Regular security updates
   - Monitor access logs:
     ```bash
     # Check logs
     cat logs/app.log
     cat logs/error.log
     ```

### Maintenance

1. **Regular Updates**
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update database schema
alembic upgrade head

# Update Docker images
docker-compose pull
```

2. **Backup Process**
```bash
# Database backup
pg_dump -U your_username -d rfm_insights > backup.sql

# Environment backup
cp .env .env.backup
```

3. **Monitoring**
- Check logs in `logs/` directory:
  ```bash
  # Latest logs
  tail -f logs/app.log
  ```
- Monitor API usage
- Check disk space regularly:
  ```bash
  # Windows
  wmic logicaldisk get name,size,freespace
  # Linux
  df -h
  ```
- Monitor database performance:
  ```bash
  # Connect to PostgreSQL
  psql -U postgres -d rfm_insights
  # Check active connections
  SELECT count(*) FROM pg_stat_activity;
  ```

### Support and Resources

1. **Getting Help**
   - Check documentation in `docs/`
   - Review troubleshooting guide
   - Contact support: support@rfminsights.com
   - GitHub issues for bug reports

2. **Useful Commands**
```bash
# View logs
docker-compose logs

# Restart services
docker-compose restart

# Check status
docker-compose ps

# Stop all services
docker-compose down
```

3. **Development Tools**
   - API documentation: http://localhost:8000/docs
   - Database admin: http://localhost:5050
   - Monitoring: http://localhost:3000

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

Seu Nome - [@seu_twitter](https://twitter.com/grsantoss) - george@rtz.com.br

Link do Projeto: [https://github.com/grsantoss/matriz-rfm](https://github.com/grsantoss/matriz-rfm)

## Features

- User authentication and authorization
- Secure API key management
- RFM analysis with customizable parameters
- Interactive visualizations
- Customer segmentation insights
- Data import/export capabilities
- Multi-tenant architecture
- Detailed customer segmentation with 10 distinct segments
- AI-powered insights and recommendations
- Automated marketing content generation

## Technology Stack

- Backend: FastAPI (Python)
- Frontend: HTML, JavaScript
- Database: PostgreSQL
- Authentication: JWT + API Keys
- Containerization: Docker
- Reverse Proxy: Nginx
- SSL: Let's Encrypt

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- PostgreSQL 13+
- Node.js 14+ (for development)
- OpenAI API key (for AI features)

## Local Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rfm-insights.git
   cd rfm-insights
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   # Create a new PostgreSQL database
   createdb rfm_insights

   # Copy environment template and update with your settings
   cp .env.template .env
   
   # Edit .env file with your database credentials and other settings
   ```

5. Initialize the database:
   ```bash
   # Initialize Alembic
   alembic init alembic

   # Create and apply migrations
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

6. Run the development server:
   ```bash
   uvicorn backend.main:app --reload
   ```

## Production Deployment

### Windows Deployment

1. Ensure Docker Desktop is installed and running
2. Open PowerShell as Administrator
3. Navigate to the project directory
4. Run the deployment script:
   ```powershell
   .\deploy-windows.ps1
   ```
5. Verify the deployment:
   ```powershell
   .\verify-deployment.ps1
   ```

### Linux/Ubuntu Deployment

1. Configure your domain names to point to your server
2. Install Docker and Docker Compose
3. Run the deployment script:
   ```bash
   sudo bash deploy.sh
   ```

## Database Management

### Initial Setup

1. Create a new PostgreSQL database:
   ```bash
   createdb rfm_insights
   ```

2. Configure database connection in `.env`:
   ```
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=rfm_insights
   ```

3. Apply migrations:
   ```bash
   alembic upgrade head
   ```

### Creating New Migrations

When you make changes to the database models:

1. Generate a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of changes"
   ```

2. Review the generated migration in `alembic/versions/`

3. Apply the migration:
   ```bash
   alembic upgrade head
   ```

### Backup and Restore

1. Create a database backup:
   ```bash
   pg_dump -U your_username -d rfm_insights > backup.sql
   ```

2. Restore from backup:
   ```bash
   psql -U your_username -d rfm_insights < backup.sql
   ```

## API Documentation

Once the application is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Key environment variables (see `.env.template` for full list):

- `ENVIRONMENT`: development, staging, or production
- `DEBUG`: Enable/disable debug mode
- `SECRET_KEY`: JWT secret key
- `DB_*`: Database connection settings
- `API_V1_PREFIX`: API version prefix
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins

## Troubleshooting

### Database Issues

1. Connection errors:
   - Verify database credentials in `.env`
   - Check if PostgreSQL is running
   - Ensure database exists and is accessible

2. Migration errors:
   - Check migration files in `alembic/versions/`
   - Try `alembic downgrade base` and then `alembic upgrade head`
   - Review database logs

### Docker Issues

1. Container startup failures:
   - Check container logs: `docker-compose logs`
   - Verify port availability
   - Ensure sufficient system resources

2. Network issues:
   - Check Docker network configuration
   - Verify host machine firewall settings

## Support

For support, please:
1. Check the documentation
2. Review common issues in Troubleshooting
3. Open an issue on GitHub
4. Contact support at support@rfminsights.com

## RFM Segmentation

The application uses sophisticated RFM analysis to segment customers into the following categories:

1. **Champions**: Recent customers who buy often and spend the most
   - High recency, frequency, and monetary scores
   - Your best customers

2. **Loyal Customers**: Buy regularly and spend significantly
   - High frequency and monetary scores
   - Consistent and valuable customers

3. **Potential Loyal Customers**: Recent customers with average frequency
   - High recency, good frequency
   - Show promise of becoming loyal customers

4. **New Customers**: Bought recently but not frequently
   - High recency, low frequency
   - Need nurturing to become regular customers

5. **Promising Customers**: Recent customers with good monetary value
   - High recency, good monetary value
   - Show potential for high value

6. **Customers Who Need Attention**: Good recency and frequency but low spending
   - Above average recency and frequency, low monetary
   - Need strategies to increase transaction value

7. **Customers at Risk**: Haven't purchased recently
   - Low recency, good in other metrics
   - Need re-engagement strategies

8. **Customers I Can't Lose**: Made big purchases but inactive recently
   - Low recency, high monetary value
   - High-value customers needing immediate attention

9. **Hibernating Customers**: Below average in all metrics but not lost
   - Low scores but still showing some activity
   - Need reactivation strategies

10. **Lost Customers**: Lowest scores across all metrics
    - Inactive for a long time
    - May need special campaigns to reactivate

Each analysis generates an Excel file containing:
- All original customer data
- RFM scores (1-5 for each metric)
- Overall RFM score
- Segment classification
- Additional analysis metrics

## File Formats and Processing

### Input File Requirements
- Supported formats: Excel (.xlsx, .xls), CSV
- Required columns:
  - Customer ID
  - Last Purchase Date (Recency)
  - Purchase Frequency
  - Purchase Amount (Monetary)
- Additional columns are preserved in the output

### Output File Format
The analysis adds the following columns to your data:
- Recency Score (1-5)
- Frequency Score (1-5)
- Monetary Score (1-5)
- RFM Score (3-15)
- Customer Segment
- All original columns are preserved

## AI Features

The application uses OpenAI's GPT-4 to provide:

1. **Segment Insights**:
   - Detailed analysis of each customer segment
   - Behavioral pattern identification
   - Opportunity spotting
   - Risk assessment
   - Strategic recommendations

2. **Marketing Suggestions**:
   - Personalized email templates
   - Campaign ideas tailored to each segment
   - Actionable engagement strategies
   - Content recommendations

3. **Automated Content Generation**:
   - Segment-specific marketing messages
   - Customized communication templates
   - Campaign copy suggestions
   - Engagement strategies

## Prompt Management

The application uses a centralized prompt management system located in `backend/utils/prompts.py`. This file contains all AI prompts used throughout the application, making it easy to maintain and update the AI's behavior.

### Prompt Categories

1. **System Prompts**:
   - Define AI roles (analyst, marketer, copywriter)
   - Set the tone and expertise level
   - Configure response style

2. **Segment Analysis Prompts**:
   - Default analysis template
   - Segment-specific templates (champions, at-risk, etc.)
   - Customizable metrics and focus areas

3. **Marketing Suggestion Prompts**:
   - Default marketing template
   - Campaign-specific templates (reactivation, loyalty)
   - Structured output format

4. **Marketplace Content Prompts**:
   - Product descriptions
   - Email campaigns
   - Social media content

### Customizing Prompts

To modify the AI's behavior or output:

1. Open `backend/utils/prompts.py`
2. Locate the relevant prompt category
3. Edit or add prompt templates
4. Use template variables: `{variable_name}`

Example:
```python
SEGMENT_ANALYSIS = {
    "champions": """
    Analyze our Champions segment:
    Metrics: {metrics}
    Focus on: {focus_areas}
    """
}
```

### Adding New Prompts

1. Add your prompt template to the appropriate category
2. Use descriptive keys for easy reference
3. Include all necessary template variables
4. Document any special formatting requirements

Example:
```python
MARKETPLACE_CONTENT = {
    "new_template": """
    Generate content for:
    {purpose}
    Target: {audience}
    Style: {style}
    """
}
```

## Configuration

### OpenAI Setup

1. Get your API key from OpenAI:
   - Visit https://platform.openai.com/
   - Create an account or log in
   - Navigate to API Keys
   - Create a new secret key

2. Configure OpenAI settings in `.env`:
   ```
   OPENAI_API_KEY=your-api-key-here
   OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo for lower cost
   OPENAI_MAX_TOKENS=800
   OPENAI_TEMPERATURE=0.7
   ```

3. Optional: Adjust model parameters
   - Temperature: Controls creativity (0.0-1.0)
   - Max tokens: Limits response length
   - Model: Choose between GPT-4 (better) or GPT-3.5 (faster/cheaper)

### Cost Considerations

The application uses OpenAI's API which has associated costs:
- GPT-4: Higher quality, more expensive
- GPT-3.5: Lower cost, still good quality
- Costs are based on token usage
- Monitor usage through OpenAI dashboard 