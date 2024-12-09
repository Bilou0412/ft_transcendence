#!/bin/bash
set -e

# Charger les variables d'environnement depuis le fichier .env
export $(grep -v '^#' /app/.env | xargs)

# Vérifier que les variables nécessaires sont définies
if [[ -z "${DB_NAME}" || -z "${DB_USER}" || -z "${DB_PASSWORD}" ]]; then
  echo "Erreur : DB_NAME, DB_USER et DB_PASSWORD doivent être définis dans le fichier .env"
  exit 1
fi

# Définir les variables nécessaires pour PostgreSQL
export POSTGRES_DB=${DB_NAME}
export POSTGRES_USER=${DB_USER}
export POSTGRES_PASSWORD=${DB_PASSWORD}

# Lancer PostgreSQL
exec docker-entrypoint.sh postgres
