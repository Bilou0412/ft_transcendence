#!/bin/sh

# Exécute les migrations
python manage.py migrate

# Démarre le serveur de développement
exec gunicorn --bind 0.0.0.0:8000 auth.wsgi:application