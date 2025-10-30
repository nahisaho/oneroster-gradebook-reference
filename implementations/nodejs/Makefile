.PHONY: help build up down logs test clean dev restart

# Default target
help:
	@echo "OneRoster Gradebook Node.js - Docker Commands"
	@echo ""
	@echo "Usage:"
	@echo "  make build       - Build Docker images"
	@echo "  make up          - Start services (production mode)"
	@echo "  make down        - Stop services"
	@echo "  make logs        - View logs"
	@echo "  make test        - Run tests in Docker"
	@echo "  make clean       - Remove containers, volumes, and images"
	@echo "  make dev         - Start in development mode (hot reload)"
	@echo "  make restart     - Restart services"
	@echo "  make shell       - Open shell in app container"
	@echo "  make db-shell    - Open PostgreSQL shell"

# Build Docker images
build:
	@echo "Building Docker images..."
	docker compose build

# Start services (production)
up:
	@echo "Starting services..."
	docker compose up -d
	@echo "Waiting for services to be healthy..."
	@sleep 5
	@echo "Services started!"
	@echo "API: http://localhost:3000"
	@echo "Health: http://localhost:3000/health"

# Stop services
down:
	@echo "Stopping services..."
	docker compose down

# View logs
logs:
	docker compose logs -f

# Run tests
test:
	@echo "Running tests in Docker..."
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@echo "Cleaning up test containers..."
	docker compose -f docker-compose.test.yml down -v

# Clean everything
clean:
	@echo "Cleaning up..."
	docker compose down -v --rmi all
	docker compose -f docker-compose.test.yml down -v --rmi all
	@echo "Cleanup complete!"

# Development mode
dev:
	@echo "Starting in development mode..."
	docker compose --profile dev up app-dev
	@echo "Development server started with hot reload!"

# Restart services
restart:
	@echo "Restarting services..."
	docker compose restart

# Open shell in app container
shell:
	docker exec -it oneroster-nodejs sh

# Open PostgreSQL shell
db-shell:
	docker exec -it oneroster-postgres psql -U postgres -d oneroster_gradebook

# Check service status
status:
	docker compose ps

# View application logs only
app-logs:
	docker compose logs -f app

# View database logs only
db-logs:
	docker compose logs -f postgres
