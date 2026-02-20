# Variables
COMPOSE = docker compose
PROJECT_NAME = sowit-fullstack-challenge
DB_DATA_DIR = ./db-data

.PHONY: up down restart build logs status clean fclean deep-clean clean-reset reset migrations migrate superuser bash-backend bash-frontend bash-db sql

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

# "Local Clean": Keeps source code, removes generated artifacts and resets app migrations

# Clean Reset: wipes bind-mounted DB data + plot migrations, then rebuilds schema from scratch
clean-reset:
	@echo "☢️  Nuclear reset starting..."
	$(COMPOSE) down
	sudo rm -rf $(DB_DATA_DIR)
	find backend/plots/migrations -type f -name "*.py" ! -name "__init__.py" -delete
	find backend/plots/migrations -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

reset: fclean clean-reset
	@echo "✅ Reset complete."

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
