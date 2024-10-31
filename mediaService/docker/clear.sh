#!/bin/bash

# Supprime tous les conteneurs Docker
docker rm -f $(docker ps -aq)

# Supprime toutes les images Docker
docker rmi -f $(docker images -q)

# Supprime tous les volumes Docker
docker volume rm -f $(docker volume ls -q)

# Supprime tous les réseaux Docker
docker network rm $(docker network ls -q)

echo "Tous les conteneurs, images, volumes et réseaux Docker ont été supprimés."