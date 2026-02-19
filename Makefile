# Variables
COMPOSE = docker compose
PROJECT_NAME = sowit-fullstack-challenge

# Files to protect from deletion in deep-clean
BACKEND_KEEP = ! -name 'Dockerfile' ! -name 'entrypoint.sh' ! -name 'requirements.txt'
FRONTEND_KEEP = ! -name 'Dockerfile' ! -name 'entrypoint.sh'

.PHONY: up down restart build logs status clean fclean deep-clean reset migrations migrate superuser bash-backend bash-frontend bash-db sql

# 1. Standard Operations
up:
	@echo "🚀 Starting containers..."
	$(COMPOSE) up -d

down:
	@echo "🛑 Stopping containers..."
	$(COMPOSE) down

restart:
	@echo "♻️  Rebuilding and restarting..."
	$(COMPOSE) down
	$(COMPOSE) up -d --build

build:
	$(COMPOSE) build

# 2. Monitoring
logs:
	$(COMPOSE) logs -f

status:
	$(COMPOSE) ps

# 3. Cleaning Rules
clean:
	$(COMPOSE) down --remove-orphans

fclean:
	@echo "🧨 Wiping Volumes & Images..."
	$(COMPOSE) down -v --rmi all --remove-orphans

deep-clean:
	@echo "📂 Scrubbing local code folders..."
	@find backend -mindepth 1 $(BACKEND_KEEP) -exec rm -rf {} +
	@find frontend -mindepth 1 $(FRONTEND_KEEP) -exec rm -rf {} +
	@rm -rf frontend/.vite frontend/.next
	@echo "✅ Local folders cleaned."

reset: fclean deep-clean
	@echo "🚀 Project factory reset complete."

# 4. Django Helpers
migrations:
	@echo "📝 Creating migrations..."
	$(COMPOSE) exec backend python manage.py makemigrations

migrate:
	@echo "📦 Applying migrations..."
	$(COMPOSE) exec backend python manage.py migrate

superuser:
	$(COMPOSE) exec backend python manage.py createsuperuser

# 5. Container Access
bash-backend:
	$(COMPOSE) exec backend /bin/bash

bash-frontend:
	$(COMPOSE) exec frontend sh

bash-db:
	$(COMPOSE) exec db /bin/bash

# Updated SQL rule: Note the PGPASSWORD env var to skip the prompt
# Replace 'sowit_password' with whatever is in your .env
sql:
	$(COMPOSE) exec -e PGPASSWORD=sowit_password db psql -h localhost -U sowit_user -d sowit_db