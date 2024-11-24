from django.contrib import admin
from .models import UserProfile, MatchHistory, Friendship, Match

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nb_game', 'nb_win', 'nb_losses', 'avg_duration')
    search_fields = ('user_id',)
    list_filter = ('nb_game', 'nb_win', 'nb_losses')
    ordering = ('-nb_game',)  # Trier par nombre de jeux décroissant
    list_per_page = 20  # Afficher 20 éléments par page
    fields = ('user_id', 'nb_game', 'nb_win', 'nb_losses', 'avg_duration')  # Contrôle des champs affichés

@admin.register(MatchHistory)
class MatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('player_1', 'player_2', 'date_of_match', 'score_player_1', 'score_player_2', 'winner', 'duration')
    search_fields = ('player_1__user_id', 'player_2__user_id')  # Recherche par les IDs des joueurs
    list_filter = ('date_of_match', 'winner')  # Filtrer par date du match et gagnant
    ordering = ('-date_of_match',)  # Trier par date du match décroissante
    list_per_page = 20  # Afficher 20 éléments par page
    fields = ('player_1', 'player_2', 'date_of_match', 'score_player_1', 'score_player_2', 'winner', 'duration')

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user_1', 'user_2', 'status', 'created_at')
    search_fields = ('user_1__user_id', 'user_2__user_id')  # Recherche par les IDs des utilisateurs
    list_filter = ('status', 'created_at')  # Filtrer par statut d'amitié et date de création
    ordering = ('-created_at',)  # Trier par date de création décroissante
    list_per_page = 20  # Afficher 20 éléments par page
    fields = ('user_1', 'user_2', 'status', 'created_at')  # Contrôle des champs affichés

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('player_1', 'player_2', 'status', 'created_at', 'match_start_time', 'match_end_time', 'confirmed_by_player_1', 'confirmed_by_player_2')
    search_fields = ('player_1__user_id', 'player_2__user_id')  # Recherche par les IDs des joueurs
    list_filter = ('status', 'created_at')  # Filtrer par statut du match et date de création
    ordering = ('-created_at',)  # Trier par date de création décroissante
    list_per_page = 20  # Afficher 20 éléments par page
    fields = ('player_1', 'player_2', 'status', 'created_at', 'match_start_time', 'match_end_time', 'confirmed_by_player_1', 'confirmed_by_player_2')  # Champs affichés

