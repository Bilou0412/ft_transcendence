from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'username', 'Student', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'Student')
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    # Champs visibles pour les utilisateurs dans l'admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'new_email', 'Student', 'otp_secret')}),  # Ajout de `otp_secret` et `mfa`
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    # Champs visibles lors de l'ajout d'un nouvel utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'username', 'Student', 'otp_secret'),  # Ajout de `otp_secret` et `mfa`
        }),
    )

# Enregistrer le modèle utilisateur personnalisé
admin.site.register(User, CustomUserAdmin)
