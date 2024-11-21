# Variables
COMPOSE = docker compose
SERVICE_DIRS := $(wildcard *-service)
COMPOSE_FILES := $(wildcard *-service/docker-compose.yml)
COMPOSE_FILE_ARGS := $(foreach file,$(COMPOSE_FILES),-f $(file))

# Colors for better readability
GREEN = \033[0;32m
RED = \033[0;31m
NC = \033[0m

# Phony targets
.PHONY: help up down logs clean

help:
	@echo "$(GREEN)Available commands:$(NC)"
	@echo " make up - Start all services"
	@echo " make down - Stop all services"
	@echo " make logs - View logs"
	@echo " make clean - Remove containers and volumes"

up:
	@echo "$(GREEN)Starting all services...$(NC)"
	$(COMPOSE) $(COMPOSE_FILE_ARGS) up --build

down:
	@echo "$(GREEN)Stopping all services...$(NC)"
	$(COMPOSE) $(COMPOSE_FILE_ARGS) down

logs:
	@echo "$(GREEN)Showing logs for all services...$(NC)"
	$(COMPOSE) $(COMPOSE_FILE_ARGS) logs

clean:
	@echo "$(RED)Cleaning up...$(NC)"
	$(COMPOSE) $(COMPOSE_FILE_ARGS) down -v --remove-orphans

fclean: clean
	-rm -r media-service/images/users_images
	@echo "$(RED)⚠️  Attention : Suppression complète de tous les éléments Docker...$(NC)"
	@echo "$(YELLOW)Suppression des conteneurs...$(NC)"
	-docker rm -f $$(docker ps -aq) 2>/dev/null || true
	@echo "$(YELLOW)Suppression des images du projet...$(NC)"
	-docker rmi -f $$(docker images | grep "auth-service\|media-service\|postgres" | awk '{print $$3}') 2>/dev/null || true
	@echo "$(YELLOW)Suppression des volumes...$(NC)"
	-docker volume rm $$(docker volume ls -q) 2>/dev/null || true
	@echo "$(YELLOW)Suppression des réseaux...$(NC)"
	-docker network rm $(docker network ls -q) 2>/dev/null || true
	@echo "$(RED)Nettoyage complet terminé$(NC)"
