.PHONY: help build up down logs test clean restart

# Default target
help:
	@echo "OneRoster Gradebook Service - Java Implementation"
	@echo ""
	@echo "Available commands:"
	@echo "  make build          - Build Docker images"
	@echo "  make up             - Start all services"
	@echo "  make down           - Stop all services"
	@echo "  make logs           - View logs"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make restart        - Restart all services"
	@echo "  make dev            - Start in development mode"
	@echo "  make shell          - Open shell in app container"
	@echo "  make db-shell       - Open PostgreSQL shell"

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Start in development mode with hot reload
dev:
	docker-compose -f docker-compose.dev.yml up

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f app

# Run tests inside container
test:
	docker-compose exec app ./mvnw test

# Run tests with coverage
coverage:
	docker-compose exec app ./mvnw clean test jacoco:report
	@echo "Coverage report: target/site/jacoco/index.html"

# Clean build artifacts
clean:
	./mvnw clean
	docker-compose down -v

# Restart services
restart: down up

# Open shell in app container
shell:
	docker-compose exec app sh

# Open PostgreSQL shell
db-shell:
	docker-compose exec db psql -U oneroster_user -d oneroster_gradebook

# Build and run
all: build up logs

# Run without Docker (local development)
run-local:
	./mvnw spring-boot:run

# Run tests locally
test-local:
	./mvnw test

# Package JAR
package:
	./mvnw clean package

# Check health
health:
	@curl -f http://localhost:8082/actuator/health || echo "Service not ready"

# View application logs only
app-logs:
	docker-compose logs -f app

# View database logs only
db-logs:
	docker-compose logs -f db
