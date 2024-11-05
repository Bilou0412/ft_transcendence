# Variables
COMPOSE = docker-compose
COMPOSE_FILE = docker-compose.yml
COMPOSE_DEV = docker-compose_dev.yml
COMPOSE_PROD = docker-compose_prod.yml

# Couleurs pour une meilleure lisibilité
GREEN = \033[0;32m
RED = \033[0;31m
YELLOW = \033[1;33m
NC = \033[0m # No Color
BOLD = \033[1m

# Commandes de base
.PHONY: help dev prod all stop clean fclean logs-dev logs-prod

help:
	@echo "$(BOLD)Usage:$(NC)"
	@echo "  $(GREEN)make dev$(NC)     - Lance l'environnement de développement"
	@echo "  $(GREEN)make prod$(NC)    - Lance l'environnement de production"
	@echo "  $(GREEN)make all$(NC)     - Lance les deux environnements"
	@echo "  $(GREEN)make stop$(NC)    - Arrête tous les conteneurs"
	@echo "  $(GREEN)make clean$(NC)   - Arrête et supprime les conteneurs, volumes et réseaux du projet"
	@echo "  $(RED)make fclean$(NC)  - Suppression complète : conteneurs, volumes, réseaux, images"
	@echo "  $(GREEN)make logs-dev$(NC) - Affiche les logs de développement"
	@echo "  $(GREEN)make logs-prod$(NC)- Affiche les logs de production"

# Environnement de développement
dev:
	@echo "$(GREEN)Lancement de l'environnement de développement...$(NC)"
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_DEV) up --build
	@echo "$(GREEN)Services de développement lancés sur:$(NC)"
	@echo "  - Auth Service: http://localhost:8000"
	@echo "  - Media Service: http://localhost:8001"

# Environnement de production
prod:
	@echo "$(GREEN)Lancement de l'environnement de production...$(NC)"
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_PROD) up --build
	@echo "$(GREEN)Services de production lancés sur:$(NC)"
	@echo "  - Auth Service: http://localhost:8000"
	@echo "  - Media Service: http://localhost:8001"

# Lance les deux environnements (dev et prod sur des ports différents)
all: dev prod

# Arrête tous les conteneurs
stop:
	@echo "$(GREEN)Arrêt des conteneurs...$(NC)"
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_DEV) down
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_PROD) down

# Nettoie les conteneurs, volumes et réseaux du projet
clean:
	@echo "$(GREEN)Nettoyage complet du projet...$(NC)"
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_DEV) down -v --remove-orphans
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_PROD) down -v --remove-orphans
	@echo "$(GREEN)Nettoyage terminé$(NC)"

# Suppression complète (conteneurs, volumes, réseaux, images)
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
	@echo "$(GREEN)Pour reconstruire le projet, utilisez 'make dev' ou 'make prod'$(NC)"

# Logs des conteneurs
logs-dev:
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_DEV) logs -f

logs-prod:
	$(COMPOSE) -f $(COMPOSE_FILE) -f $(COMPOSE_PROD) logs -f