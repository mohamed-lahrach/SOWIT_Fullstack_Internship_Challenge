# Variables
COMPOSE = docker compose
PROJECT_NAME = sowit-fullstack-challenge
DB_DATA_DIR = ./db-data
SHELL_CMD ?= /bin/bash

ifneq (,$(wildcard ./.env))
include .env
export
endif

.PHONY: \
	up down restart build \
	logs status \
	clean fclean clean-reset reset \
	init migrations migrate test superuser \
	bash-backend bash-frontend bash-db shell sql \
	scaffold-project scaffold-app scaffold-frontend

# Lifecycle
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

# Monitor
status:
	$(COMPOSE) ps

logs:
	@if [ -z "$(SERVICE)" ]; then echo "❌ Error: SERVICE is required. Use 'make logs SERVICE=backend'"; exit 1; fi
	$(COMPOSE) logs -f $(SERVICE)

# Cleanup
clean:
	$(COMPOSE) down --remove-orphans

fclean:
	@echo "🧨 Wiping Volumes & Images..."
	$(COMPOSE) down -v --rmi all --remove-orphans

# Clean Reset: wipes bind-mounted DB data + plot migrations, then rebuilds schema from scratch
clean-reset:
	@echo "☢️  Nuclear reset starting..."
	$(COMPOSE) down
	sudo rm -rf $(DB_DATA_DIR)
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +

reset: fclean clean-reset
	@echo "✅ Reset complete."

# Backend
init:
	$(MAKE) up
	$(MAKE) migrations
	$(MAKE) migrate
	@echo "✅ Init complete."

migrations:
	@echo "📝 Creating migrations..."
	$(COMPOSE) exec backend python manage.py makemigrations

migrate:
	@echo "📦 Applying migrations..."
	$(COMPOSE) exec backend python manage.py migrate

test:
	@echo "🧪 Running backend tests..."
	$(COMPOSE) exec -T backend python manage.py test

superuser:
	$(COMPOSE) exec backend python manage.py createsuperuser

# Access
bash-backend:
	$(MAKE) shell SERVICE=backend SHELL_CMD=/bin/bash

bash-frontend:
	$(MAKE) shell SERVICE=frontend SHELL_CMD=sh

bash-db:
	$(MAKE) shell SERVICE=db SHELL_CMD=/bin/bash

shell:
	@if [ -z "$(SERVICE)" ]; then echo "❌ Error: SERVICE is required. Use 'make shell SERVICE=backend'"; exit 1; fi
	$(COMPOSE) exec $(SERVICE) $(SHELL_CMD)

sql:
	@if [ -z "$(POSTGRES_USER)" ] || [ -z "$(POSTGRES_PASSWORD)" ] || [ -z "$(POSTGRES_DB)" ]; then \
		echo "❌ Error: POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB must be set (e.g. in .env)."; \
		exit 1; \
	fi
	$(COMPOSE) exec -e PGPASSWORD=$(POSTGRES_PASSWORD) db psql -h localhost -U $(POSTGRES_USER) -d $(POSTGRES_DB)

# Scaffold
# Usage: make scaffold-project
# Creates 'core' settings folder and manage.py in the root
scaffold-project:
	@echo "🏗️  Scaffolding new Django Project..."
	$(COMPOSE) exec backend django-admin startproject core .
	@echo "✅ Project 'core' created. Restarting container to apply settings..."
	$(COMPOSE) restart backend

# Usage: make scaffold-app NAME=plots
# Creates a new Django app
scaffold-app:
	if [ -z "$(NAME)" ]; then echo "❌ Error: NAME is required. Use 'make scaffold-app NAME=myapp'"; exit 1; fi
	@echo "🏗️  Scaffolding App: $(NAME)..."
	$(COMPOSE) exec backend python manage.py startapp $(NAME)
	@echo "✅ App '$(NAME)' created."

# Usage: make scaffold-frontend
# Interactive command to create a React app in the current folder
scaffold-frontend:
	@echo "🏗️  Scaffolding React Frontend..."

	# We use '-- --template react' to skip prompts, and '.' to use current dir.
	# Note: If the directory is not empty (it has Dockerfile), Vite might warn.
	# We use 'create-vite .' and let the user handle the prompt if needed.
	
	$(COMPOSE) exec -it frontend npm create vite@latest . -- --template react
	@echo "✅ Frontend created. Restarting to install dependencies..."
	$(COMPOSE) restart frontend
