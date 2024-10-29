#!/bin/sh

# Exécute les migrations
python manage.py migrate

# Crée un superutilisateur si aucun n'existe
echo "Création du superutilisateur..."
python manage.py shell << END
from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print("Superutilisateur créé avec succès !")
else:
    print("Le superutilisateur existe déjà.")
END

# Démarre le serveur de développement
exec python manage.py runserver 0.0.0.0:8000