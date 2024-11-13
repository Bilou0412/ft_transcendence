from django.db import models

class UserProfile (models.Model):
    user_id = models.IntegerField(unique=True)
    nb_game = models.IntegerField(default=0)
    nb_win = models.IntegerField(default=0)
    nb_losses = models.IntegerField(default=0)
    avg_duration = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"Profile of user {self.user_id}"