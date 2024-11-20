from django.db import models

class UserProfile (models.Model):
    user_id = models.IntegerField(unique=True)
    nb_game = models.IntegerField(default=0)
    nb_win = models.IntegerField(default=0)
    nb_losses = models.IntegerField(default=0)
    avg_duration = models.FloatField(default=0)

    def __str__(self) -> str:
        return f"Profile of user {self.user_id}"
    
class MatchHistory(models.Model):
    player_1 = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='matches_as_player_1')
    player_2 = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='matches_as_player_2')
    date_of_match = models.DateTimeField(auto_now_add=True)
    score_player_1 = models.IntegerField()
    score_player_2 = models.IntegerField()
    winner = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='won_matches', null=True, blank=True)
    duration = models.IntegerField()  # Durée du match en secondes (ou toute autre unité que tu choisis)

    def __str__(self):
        return f"Match between {self.player_1.user_id} and {self.player_2.user_id} on {self.date_of_match}"
    
    def save(self, *args, **kwargs):
        # Calcul automatique du gagnant en fonction des scores
        if self.score_player_1 > self.score_player_2:
            self.winner = self.player_1
        elif self.score_player_2 > self.score_player_1:
            self.winner = self.player_2
        else:
            self.winner = None  # Egalité
        super().save(*args, **kwargs)
        self.update_user_profile(self.player_1)
        self.update_user_profile(self.player_2)

    def update_user_profile(self, player):
        # Mettre à jour le nombre total de jeux
        player.nb_game += 1

        # Mettre à jour le nombre de victoires et de défaites
        if self.winner == player:
            player.nb_win += 1
        elif self.winner != player and self.winner is not None:
            player.nb_losses += 1

        # Mettre à jour la durée moyenne
        total_duration = player.avg_duration * (player.nb_game - 1) + self.duration
        player.avg_duration = total_duration / player.nb_game

        # Sauvegarder le profil mis à jour
        player.save()

from django.db import models

class Friendship(models.Model):
    # Référence aux deux utilisateurs qui sont amis
    user_1 = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='friendship_user_1')
    user_2 = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='friendship_user_2')
    
    # Statut de l'amitié (par exemple, "en attente", "confirmée", etc.)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('blocked', 'Blocked')], default='pending')

    # Date de la demande d'amitié
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Assurer l'unicité de la relation (une amitié entre deux utilisateurs est unique)
    class Meta:
        unique_together = ('user_1', 'user_2')
    
    def __str__(self):
        return f"Friendship between {self.user_1} and {self.user_2} ({self.status})"
