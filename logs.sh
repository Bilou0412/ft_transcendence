#!/bin/bash
# Liste des services
services=(*-service)
# Ouvrir une fenêtre gnome-terminal par service en arrière-plan
for service in "${services[@]}"; do
  gnome-terminal -- bash -c "cd $service && docker compose logs -f; exec bash" &
done
# Attendre que tous les processus se terminent
wait