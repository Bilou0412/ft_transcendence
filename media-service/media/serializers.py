from rest_framework import serializers
from .models import UserProfileImage

class UserProfileImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    
    class Meta:
        model = UserProfileImage
        fields = ['image']
    
    def validate_image(self, value):
        max_size = 5 * 1024 * 1024  # 5 Mo
        if value:
            if value.size > max_size:
                raise serializers.ValidationError("The image must not exceed 5 Mo.")
            
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError("File type not supported. Use JPEG, PNG or GIF.")
        
        return value