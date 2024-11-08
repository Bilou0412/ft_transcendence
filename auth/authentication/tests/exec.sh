#!/bin/bash

# Vérifie si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "Docker n'est pas installé. Veuillez l'installer pour continuer."
    exit 1
fi

# Récupère l'ID du conteneur pour le service `auth-web_dev`
CONTAINER_ID=$(docker ps -qf "name=auth-web_dev")

# Vérifie si un conteneur a été trouvé
if [ -z "$CONTAINER_ID" ]; then
    echo "Le conteneur auth-web_dev n'est pas en cours d'exécution."
    exit 1
fi

# Affiche un message indiquant que les tests vont être exécutés
echo "Exécution des tests dans le conteneur auth-web_dev..."

# Exécute les tests dans le conteneur avec plus de verbosité
docker exec -it "$CONTAINER_ID" python manage.py test authentication.tests -v 2