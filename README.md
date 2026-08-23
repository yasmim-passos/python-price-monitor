# Price Monitor API

Uma API robusta para monitoramento de preços de produtos com scraping automático, sistema de alertas e cache inteligente.

## Características Principais

- **API RESTful** completa com FastAPI
- **Autenticação JWT** segura
- **Scraping assíncrono** de Mercado Livre, Amazon e sites genéricos
- **Sistema de alertas** de preço
- **Cache Redis** para otimização
- **Filas Celery** para processamento assíncrono
- **Docker Compose** para deploy fácil
- **Documentação interativa** (Swagger/OpenAPI)

## Arquitetura

```
price-monitor/
├── app/
│   ├── api/              # Endpoints da API
│   │   ├── auth.py       # Autenticação e registro
│   │   ├── products.py   # CRUD de produtos
│   │   ├── alerts.py     # Gerenciamento de alertas
│   │   └── monitor.py    # Endpoints de monitoramento
│   ├── core/             # Configurações principais
│   │   ├── config.py     # Settings
│   │   ├── database.py   # Configuração do DB
│   │   ├── security.py   # JWT e autenticação
│   │   └── cache.py      # Cliente Redis
│   ├── domain/           # Modelos de negócio
│   │   ├── models.py     # SQLAlchemy models
│   │   └── schemas.py    # Pydantic schemas
│   ├── services/         # Lógica de negócio
│   │   ├── scraper.py    # Serviço de scraping
│   │   └── monitor.py    # Serviço de monitoramento
│   └── workers/          # Tarefas assíncronas
│       └── celery_worker.py
├── docker-compose.yml    # Orquestração
├── Dockerfile
├── requirements.txt
└── README.md
```

## Quick Start

### Opção 1: Docker (Recomendado)

```bash
# Clone o repositório
git clone <seu-repo>
cd price-monitor

# Suba todos os serviços
docker-compose up -d

# Verifique os logs
docker-compose logs -f api

# Acesse a documentação interativa
open http://localhost:8000/docs
```

### Opção 2: Local

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env conforme necessário

# Instale e inicie Redis (necessário)
# Mac: brew install redis && brew services start redis
# Ubuntu: sudo apt-get install redis-server
# Windows: Use Docker ou WSL

# Execute a aplicação
uvicorn main:app --reload

# Em outro terminal, execute o worker Celery
celery -A app.workers.celery_worker worker --loglevel=info

# Em outro terminal, execute o scheduler
celery -A app.workers.celery_worker beat --loglevel=info
```

## Uso da API

### 1. Registrar um usuário

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "securepass123"
  }'
```

### 2. Fazer login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=myuser&password=securepass123"
```

Resposta:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Adicionar produto para monitorar

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15 Pro",
    "url": "https://www.mercadolivre.com.br/apple-iphone-15-pro-..."
  }'
```

### 4. Criar alerta de preço

```bash
curl -X POST "http://localhost:8000/api/v1/alerts/" \
  -H "Authorization: Bearer SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "target_price": 5999.00
  }'
```

### 5. Verificar preço manualmente

```bash
curl -X POST "http://localhost:8000/api/v1/monitor/check/1" \
  -H "Authorization: Bearer SEU_TOKEN"
```

### 6. Ver estatísticas de preço

```bash
curl -X GET "http://localhost:8000/api/v1/monitor/stats/1" \
  -H "Authorization: Bearer SEU_TOKEN"
```
## Docker Commands

```bash
# Subir todos os serviços
docker-compose up -d

# Ver logs
docker-compose logs -f api
docker-compose logs -f celery_worker

# Parar todos os serviços
docker-compose down

# Rebuild containers
docker-compose build --no-cache

# Acessar shell do container
docker-compose exec api /bin/bash

# Ver status dos serviços
docker-compose ps
```

## Monitoramento

### Flower (Celery UI)
- URL: http://localhost:5555
- Monitor tasks, workers, e estatísticas em tempo real

### API Docs (Swagger)
- URL: http://localhost:8000/docs
- Documentação interativa completa da API

### ReDoc
- URL: http://localhost:8000/redoc
- Documentação alternativa

## Configuração

Principais variáveis de ambiente (`.env`):

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=your-super-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Scraping
SCRAPING_INTERVAL_MINUTES=60
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

## Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **Pydantic** - Validação de dados
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e message broker
- **Celery** - Filas de tarefas assíncronas
- **BeautifulSoup4** - Web scraping
- **HTTPX** - Cliente HTTP assíncrono
- **pytest** - Framework de testes
- **Docker** - Containerização

## Roadmap

- [ ] Suporte a mais sites de e-commerce
- [ ] Notificações por email quando alertas são acionados
- [ ] Dashboard web com gráficos de histórico de preços
- [ ] API de webhooks para integrações
- [ ] Suporte a múltiplas moedas
- [ ] Sistema de categorias de produtos
- [ ] Exportação de dados (CSV, Excel)

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT.

---

**Dica:** Para ambientes de produção, configure:
- Variáveis de ambiente seguras
- SSL/TLS
- Rate limiting
- Logging centralizado
- Monitoring (Prometheus, Grafana)
- Backup automático do banco de dados
