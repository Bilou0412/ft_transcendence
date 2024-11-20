from django.contrib import admin
from .models import UserProfile, MatchHistory ,Friendship

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nb_game', 'nb_win', 'nb_losses', 'avg_duration')
    search_fields = ('user_id',)
    list_filter = ('nb_game',)

@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('player_1', 'player_2', 'date_of_match', 'score_player_1', 'score_player_2', 'winner', 'duration')
    search_fields = ('player_1__user_id', 'player_2__user_id')  # Recherche par les IDs des joueurs
    list_filter = ('date_of_match', 'winner')  # Filtrer par date du match et gagnant

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user_1', 'user_2', 'status', 'created_at')
    search_fields = ('user_1__user_id', 'user_2__user_id')  # Recherche par les IDs des utilisateurs
    list_filter = ('status', 'created_at')  # Filtrer par statut d'amitié et date de création
