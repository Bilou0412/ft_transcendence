from django.contrib import admin
from .models import User  # Importez votre modèle personnalisé User

class CustomUserAdmin(admin.ModelAdmin):
    model = User
    list_display = ['username', 'email', 'new_email', 'is_active', 'date_joined']
    search_fields = ['username', 'email', 'new_email']
    ordering = ['username']

# Ne désenregistrez pas le modèle si il n'est pas encore enregistré
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass  # Si le modèle n'est pas enregistré, ignorez l'erreur

admin.site.register(User, CustomUserAdmin)  # Enregistrez votre modèle personnalisé
