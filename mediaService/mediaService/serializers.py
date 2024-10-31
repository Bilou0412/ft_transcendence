from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfileImage

class UserProfileImageSerializer(serializers.ModelSerializer):
    # username = serializers.CharField(write_only=True)
    image = serializers.ImageField(required=False)  # Rend l'image optionnelle
    
    class Meta:
        model = UserProfileImage
        fields = ['image']
    
    def validate_image(self, value):
        # Validation personnalisée de l'image (optionnel)
        max_size = 5 * 1024 * 1024  # 5 Mo
        if value:
            if value.size > max_size:
                raise serializers.ValidationError("La taille de l'image ne doit pas dépasser 5 Mo.")
            
            # Vérification du type de fichier (optionnel)
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("Type de fichier non supporté. Utilisez JPEG, PNG ou GIF.")
        
        return value