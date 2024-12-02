# Variables
COMPOSE = docker-compose

# Find all service directories
SERVICE_DIRS := $(wildcard *-service)

# Colors for better readability
GREEN = \033[0;32m
RED = \033[0;31m
NC = \033[0m

# Phony targets
.PHONY: help up down logs clean

help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo " make up   - Start all services"
	@echo " make down - Stop all services"
	@echo " make logs - View logs"
	@echo " make clean - Remove containers and volumes"

up:
	@if ! docker network ls --format '{{.Name}}' | grep -q "^my_network$$"; then \
		echo "$(GREEN)Creating network my_network...$(NC)"; \
		docker network create my_network; \
	fi
	@echo "$(GREEN)Starting services...$(NC)"
	@for dir in $(SERVICE_DIRS); do \
		(cd $$dir && docker compose up)& \
	done
	@wait
	
down:
	@echo "$(GREEN)Stopping services...$(NC)"
	@for dir in $(SERVICE_DIRS); do \
		echo "Stopping $$dir"; \
		(cd $$dir && docker compose down); \
	done

logs:
	@echo "$(GREEN)Showing logs for all services...$(NC)"
	@for dir in $(SERVICE_DIRS); do \
		echo "Logs for $$dir:"; \
		(cd $$dir && docker compose logs -f); \
	done

clean:
	@echo "$(RED)Cleaning up...$(NC)"
	@for dir in $(SERVICE_DIRS); do \
		echo "Cleaning $$dir"; \
		(cd $$dir && docker compose down -v --remove-orphans); \
	done
	docker network rm my_network