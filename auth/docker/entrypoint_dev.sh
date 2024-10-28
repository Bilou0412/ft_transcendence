#!/bin/sh

# Exécute les migrations
python manage.py migrate

# Démarre le serveur de développement
exec python manage.py runserver 0.0.0.0:8000
