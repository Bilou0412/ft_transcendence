import os
from django.db import models
from django.contrib.auth.models import User

class UserProfileImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_image')
    # username = models.CharField(max_length=200)
    image = models.ImageField(upload_to='', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Check if the instance already has an image before saving a new one
        if self.pk:
            old_image = UserProfileImage.objects.get(pk=self.pk).image
            # Only delete the old image if a new one is being set
            if old_image and old_image != self.image:
                if os.path.isfile(old_image.path):
                    os.remove(old_image.path)
                    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image de profil de {self.username}"  
    