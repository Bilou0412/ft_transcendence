import os
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify

def unique_filename_username(instance, filename):
    extension = filename.split('.')[-1]
    username_slug = slugify(instance.user.username)
    unique_filename = f"{username_slug}_{uuid.uuid4()}.{extension}"
    return os.path.join('users_images', unique_filename)


class UserProfileImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile_image')
    image = models.ImageField(upload_to=unique_filename_username, null=True)

    def save(self, *args, **kwargs):
        if self.pk:
            old_image = UserProfileImage.objects.get(pk=self.pk).image
            if old_image and old_image != self.image:
                if os.path.isfile(old_image.path):
                    os.remove(old_image.path)
                    
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profil image of {self.username}"  
    