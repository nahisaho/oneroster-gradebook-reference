# OneRoster Gradebook Service - Python/FastAPI Implementation

IMS Global OneRoster v1.2 Gradebook Service Reference Implementation using Python, FastAPI, and PostgreSQL.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development](#development)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [OAuth 2.0 Authentication](#oauth-20-authentication)

## ✨ Features

- **OneRoster v1.2 Compliance**: Full implementation of IMS Global OneRoster Gradebook specification
- **RESTful API**: Categories, Line Items, and Results endpoints
- **OAuth 2.0**: Client Credentials Grant flow with scope-based authorization
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Validation**: Pydantic schemas for request/response validation
- **Query Support**: Filtering, sorting, pagination, and field selection
- **Rate Limiting**: Built-in rate limiting with slowapi
- **CORS Support**: Configurable Cross-Origin Resource Sharing
- **Docker Ready**: Complete containerization with docker-compose
- **Type Safety**: Full type hints with mypy support
- **Code Quality**: Black, ruff, and mypy for code quality assurance

## 🛠 Tech Stack

- **Framework**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **Validation**: Pydantic 2.5.0
- **Authentication**: Authlib 1.2.1, python-jose 3.3.0
- **Database**: PostgreSQL 12+
- **Testing**: pytest 7.4.3, httpx 0.25.2
- **Code Quality**: black, ruff, mypy
- **Containerization**: Docker, docker-compose

## 📁 Project Structure

```
implementations/python/
├── src/
│   ├── config/          # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py  # Pydantic settings
│   │   └── database.py  # Database connection
│   ├── models/          # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   └── models.py    # Category, LineItem, Result
│   ├── schemas/         # Pydantic schemas
│   │   ├── __init__.py
│   │   └── schemas.py   # Request/Response validation
│   ├── routers/         # API endpoints
│   │   ├── __init__.py
│   │   ├── categories.py
│   │   ├── line_items.py
│   │   └── results.py
│   ├── services/        # Business logic
│   │   ├── __init__.py
│   │   ├── category_service.py
│   │   ├── line_item_service.py
│   │   └── result_service.py
│   ├── middleware/      # Authentication middleware
│   │   ├── __init__.py
│   │   └── auth.py      # OAuth 2.0 implementation
│   ├── utils/           # Utility functions
│   │   ├── __init__.py
│   │   └── query_parser.py  # OneRoster query parser
│   └── main.py          # Application entry point
├── tests/               # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_categories.py
│   ├── test_line_items.py
│   ├── test_results.py
│   └── test_oauth.py
├── .env.example         # Environment template
├── .env                 # Environment configuration
├── pyproject.toml       # Poetry dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── Makefile             # Development commands
└── README.md            # This file
```

## 📦 Prerequisites

- Python 3.11 or higher
- Poetry 1.7.1 or higher
- PostgreSQL 12 or higher
- Docker and docker-compose (for containerized deployment)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
cd implementations/python

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Run tests
docker-compose exec app poetry run pytest tests/ -v

# Stop services
docker-compose down
```

The API will be available at `http://localhost:8001`

### Local Development

```bash
# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials

# Run database migrations (if using migrations)
# poetry run alembic upgrade head

# Start development server
poetry run uvicorn src.main:app --reload

# Or use make
make dev
```

The API will be available at `http://localhost:8000`

## 🔧 Development

### Install Dependencies

```bash
make install
# or
poetry install
```

### Run Development Server

```bash
make dev
# or
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Format Code

```bash
make format
# or
poetry run black src/ tests/
poetry run isort src/ tests/
```

### Run Linters

```bash
make lint
# or
poetry run ruff check src/ tests/
poetry run mypy src/
```

### Clean Up

```bash
make clean
```

## 🧪 Testing

### Test Results Summary

- **Total Tests**: 38
- **Passing**: 38 (100%) ✅
- **Coverage**: 93% ✅
- **Status**: All tests passing, production ready

See [TEST_RESULTS.md](./TEST_RESULTS.md) for detailed test results and code quality reports.

### Run All Tests

```bash
make test
# or
poetry run pytest tests/ -v
```

### Run Tests with Coverage

```bash
make test-coverage
# or
poetry run pytest tests/ -v --cov=src --cov-report=html --cov-report=term
```

### Run Specific Test File

```bash
poetry run pytest tests/test_categories.py -v
```

### Run Tests in Docker

```bash
make docker-test
# or
docker-compose exec app pytest tests/ -v
```

### Code Quality

```bash
# Format code
make format  # or: docker-compose exec app black src/ tests/

# Lint code
make lint    # or: docker-compose exec app ruff check src/ tests/

# Type check
make mypy    # or: docker-compose exec app mypy src/
```

**Quality Status**: ✅ Black formatted | ✅ Ruff clean | ✅ 100% test success | ✅ 93% coverage

## 📚 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Endpoints

#### OAuth 2.0

```
POST /oauth/token
- Grant Type: client_credentials
- Parameters: client_id, client_secret, scope
```

#### Categories

```
GET    /ims/oneroster/v1p2/categories
GET    /ims/oneroster/v1p2/categories/{sourcedId}
POST   /ims/oneroster/v1p2/categories
PUT    /ims/oneroster/v1p2/categories/{sourcedId}
DELETE /ims/oneroster/v1p2/categories/{sourcedId}
```

#### Line Items

```
GET    /ims/oneroster/v1p2/lineItems
GET    /ims/oneroster/v1p2/lineItems/{sourcedId}
POST   /ims/oneroster/v1p2/lineItems
PUT    /ims/oneroster/v1p2/lineItems/{sourcedId}
DELETE /ims/oneroster/v1p2/lineItems/{sourcedId}
```

#### Results

```
GET    /ims/oneroster/v1p2/results
GET    /ims/oneroster/v1p2/results/{sourcedId}
POST   /ims/oneroster/v1p2/results
PUT    /ims/oneroster/v1p2/results/{sourcedId}
DELETE /ims/oneroster/v1p2/results/{sourcedId}
```

## 🐳 Docker Deployment

### Build Images

```bash
make docker-build
# or
docker-compose build
```

### Start Services

```bash
make docker-up
# or
docker-compose up -d
```

### View Logs

```bash
make docker-logs
# or
docker-compose logs -f app
```

### Stop Services

```bash
make docker-down
# or
docker-compose down
```

### Access Container Shell

```bash
make docker-shell
# or
docker-compose exec app /bin/bash
```

### Access Database Shell

```bash
make db-shell
# or
docker-compose exec db psql -U oneroster_user -d oneroster_gradebook
```

## ⚙️ Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# Database
DATABASE_URL=postgresql://oneroster_user:oneroster_pass@localhost:5432/oneroster_gradebook

# Application
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# OAuth 2.0 Clients (format: client_id:client_secret:scope1,scope2)
OAUTH_CLIENT_TEST_CLIENT=test_secret:https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly,https://purl.imsglobal.org/spec/or/v1p2/scope/results.readonly,https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput,https://purl.imsglobal.org/spec/or/v1p2/scope/results.delete

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
CORS_ALLOW_CREDENTIALS=true

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
```

## 🔐 OAuth 2.0 Authentication

### Get Access Token

```bash
curl -X POST http://localhost:8001/oauth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=test_client&client_secret=test_secret&scope=https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly"
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly"
}
```

### Use Access Token

```bash
curl -X GET http://localhost:8001/ims/oneroster/v1p2/categories \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### OneRoster Scopes

- `roster-core.readonly`: Read categories and line items
- `results.readonly`: Read results
- `results.createput`: Create and update results
- `results.delete`: Delete results

## 📖 Query Examples

### Filter

```bash
# Get categories with title containing "Math"
GET /categories?filter=title~'Math'

# Get line items with weight > 0.5
GET /lineItems?filter=weight>0.5

# Multiple conditions
GET /results?filter=scoreStatus='fully graded' AND score>80
```

### Sort

```bash
# Sort by title ascending
GET /categories?sort=title

# Sort by title descending
GET /categories?sort=title DESC

# Multiple fields
GET /lineItems?sort=assignDate DESC,title ASC
```

### Pagination

```bash
# Get 20 items starting from offset 40
GET /categories?limit=20&offset=40
```

### Field Selection

```bash
# Return only specific fields
GET /categories?fields=sourcedId,title,weight
```

### Combined Query

```bash
GET /lineItems?filter=classSourcedId='CLASS123'&sort=dueDate DESC&limit=50&offset=0&fields=sourcedId,title,dueDate
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Format code (`make format`)
5. Run linters (`make lint`)
6. Run tests (`make test`)
7. Commit changes (`git commit -m 'Add amazing feature'`)
8. Push to branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📄 License

This project is part of the OneRoster Gradebook Reference Implementation.

## 🔗 Links

- [IMS Global OneRoster v1.2 Specification](https://www.imsglobal.org/spec/oneroster/v1p2)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## 📞 Support

For issues and questions:
- Create an issue in the repository
- Refer to the OneRoster specification
- Check the API documentation at `/docs`
