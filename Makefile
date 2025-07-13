# Digital Twin Platform Makefile
# Provides convenient commands for development and deployment

.PHONY: help dev prod build clean logs test lint format install

# Default target
help:
	@echo "Digital Twin Platform - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  make dev          - Start development environment"
	@echo "  make dev-down     - Stop development environment"
	@echo "  make dev-logs     - View development logs"
	@echo "  make dev-clean    - Clean development environment"
	@echo ""
	@echo "Production:"
	@echo "  make prod         - Start production environment"
	@echo "  make prod-down    - Stop production environment"
	@echo "  make prod-logs    - View production logs"
	@echo "  make prod-clean   - Clean production environment"
	@echo ""
	@echo "Building:"
	@echo "  make build        - Build all Docker images"
	@echo "  make build-backend - Build backend image"
	@echo "  make build-frontend - Build frontend image"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean all Docker resources"
	@echo "  make logs         - View all logs"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linting"
	@echo "  make format       - Format code"
	@echo "  make install      - Install dependencies"

# Development Environment
dev:
	@echo "Starting development environment..."
	cd infra/docker && docker-compose -f docker-compose.dev.yml up -d
	@echo "Development environment started!"
	@echo "Services available at:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - Redis: localhost:6379"
	@echo "  - MQTT: localhost:1883"
	@echo "  - pgAdmin: http://localhost:5050"
	@echo "  - Redis Commander: http://localhost:8081"
	@echo "  - MQTT Explorer: http://localhost:4000"

dev-down:
	@echo "Stopping development environment..."
	cd infra/docker && docker-compose -f docker-compose.dev.yml down

dev-logs:
	cd infra/docker && docker-compose -f docker-compose.dev.yml logs -f

dev-clean:
	@echo "Cleaning development environment..."
	cd infra/docker && docker-compose -f docker-compose.dev.yml down -v --remove-orphans
	docker system prune -f

# Production Environment
prod:
	@echo "Starting production environment..."
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Please copy .env.example to .env and configure it."; \
		exit 1; \
	fi
	cd infra/docker && docker-compose -f docker-compose.prod.yml up -d
	@echo "Production environment started!"
	@echo "Services available at:"
	@echo "  - Frontend: http://localhost:80"
	@echo "  - Backend API: http://localhost:8000"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"

prod-down:
	@echo "Stopping production environment..."
	cd infra/docker && docker-compose -f docker-compose.prod.yml down

prod-logs:
	cd infra/docker && docker-compose -f docker-compose.prod.yml logs -f

prod-clean:
	@echo "Cleaning production environment..."
	cd infra/docker && docker-compose -f docker-compose.prod.yml down -v --remove-orphans
	docker system prune -f

# Building
build:
	@echo "Building all Docker images..."
	cd infra/docker && docker-compose -f docker-compose.prod.yml build --no-cache

build-backend:
	@echo "Building backend image..."
	cd backend && docker build -t digital-twin-backend .

build-frontend:
	@echo "Building frontend image..."
	cd frontend && docker build -t digital-twin-frontend .

# Maintenance
clean:
	@echo "Cleaning all Docker resources..."
	docker system prune -af --volumes
	docker network prune -f

logs:
	@echo "Viewing all logs..."
	cd infra/docker && docker-compose -f docker-compose.prod.yml logs -f

test:
	@echo "Running tests..."
	cd backend && python -m pytest tests/ -v
	cd frontend && npm test

lint:
	@echo "Running linting..."
	cd backend && python -m flake8 . --max-line-length=100
	cd frontend && npm run lint

format:
	@echo "Formatting code..."
	cd backend && python -m black . --line-length=100
	cd frontend && npm run format

install:
	@echo "Installing dependencies..."
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# Database operations
db-migrate:
	@echo "Running database migrations..."
	cd backend && python -m alembic upgrade head

db-reset:
	@echo "Resetting database..."
	cd infra/docker && docker-compose -f docker-compose.dev.yml exec postgres psql -U postgres -d digital_twin_dev -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
	make db-migrate

# Monitoring
monitor:
	@echo "Opening monitoring dashboards..."
	@echo "Grafana: http://localhost:3000 (admin/admin)"
	@echo "Prometheus: http://localhost:9090"

# Backup and restore
backup:
	@echo "Creating database backup..."
	cd infra/docker && docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U postgres digital_twin > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file path: " backup_file; \
	cd infra/docker && docker-compose -f docker-compose.prod.yml exec -T postgres psql -U postgres digital_twin < $$backup_file

# Security scan
security-scan:
	@echo "Running security scan..."
	docker run --rm -v $(PWD):/app securecodewarrior/docker-security-scan /app

# Performance test
perf-test:
	@echo "Running performance tests..."
	cd tests && python performance_test.py

