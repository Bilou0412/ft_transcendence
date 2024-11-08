from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    new_email = models.EmailField(null=True, blank=True)  # Ajout du champ temporaire pour le nouvel email
    Student = models.BooleanField(default=False)
    NoStudent = models.BooleanField(default=False)