# Variables
COMPOSE = docker compose
SERVICE_DIRS := $(wildcard *-service)
NETWORK = my_network

# Colors
GREEN = \033[0;32m
RED = \033[0;31m
NC = \033[0m

# Phony targets
.PHONY: help up down logs clean create-network logs-terminator

help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo " make up             - Start all services"
	@echo " make down           - Stop all services"
	@echo " make logs           - View logs"
	@echo " make logs-terminator - View logs in Terminator (one pane per service)"
	@echo " make clean          - Remove containers and volumes"

create-network:
	@if ! docker network ls --format '{{.Name}}' | grep -q "^$(NETWORK)$$"; then \
		echo "$(GREEN)Creating network $(NETWORK)...$(NC)"; \
		docker network create $(NETWORK); \
	fi

up: create-network
	@echo "$(GREEN)Starting services...$(NC)"
	@$(foreach dir, $(SERVICE_DIRS), \
		(echo "Starting $(dir)"; cd $(dir) && $(COMPOSE) up -d) &&) true

down:
	@echo "$(GREEN)Stopping services...$(NC)"
	@$(foreach dir, $(SERVICE_DIRS), \
		(echo "Stopping $(dir)"; cd $(dir) && $(COMPOSE) down) &&) true

logs:
	@echo "$(GREEN)Opening GNOME Terminal with tabs for all services...$(NC)"
	@$(foreach dir, $(SERVICE_DIRS), \
		(cd $(dir) && $(COMPOSE) logs -f) &) true
  		# (gnome-terminal -- bash -c "cd $(dir) && docker compose logs -f; exec bash" &) &&) true


clean: down
	@echo "$(RED)Cleaning up...$(NC)"
	@$(foreach dir, $(SERVICE_DIRS), \
		(echo "Cleaning $(dir)"; cd $(dir) && $(COMPOSE) down -v --remove-orphans) &&) true
	@docker network rm $(NETWORK) || true