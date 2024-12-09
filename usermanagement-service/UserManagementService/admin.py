from django.contrib import admin
from .models import UserProfile, Friendship, Match, BlockedUser

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'nb_game', 'nb_win', 'nb_losses', 'avg_duration')
    search_fields = ('user_id',)
    list_filter = ('nb_game', 'nb_win', 'nb_losses')
    ordering = ('-nb_game',)  # Trier par nombre de jeux décroissant
    list_per_page = 20  # Afficher 20 éléments par page
    fields = ('user_id', 'nb_game', 'nb_win', 'nb_losses', 'avg_duration')  # Contrôle des champs affichés


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('user_1', 'user_2', 'status', 'created_at')
    search_fields = ('user_1__user_id', 'user_2__user_id')
    list_filter = ('status', 'created_at')
    ordering = ('-created_at',) 
    fields = ('user_1', 'user_2', 'status', 'created_at') 
    readonly_fields = ('created_at',) 
    list_per_page = 20


@admin.register(BlockedUser)
class BlockedUserAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked', 'created_at')
    search_fields = ('blocker__user_id', 'blocked__user_id')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    list_per_page = 20

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    # Champs affichés dans la liste des matchs
    list_display = (
        'id', 
        'player_1', 
        'player_2', 
        'created_at', 
        'match_start_time', 
        'match_end_time', 
        'score_player_1', 
        'score_player_2'
    )
    # Recherche par IDs des joueurs
    search_fields = ('player_1__user_id', 'player_2__user_id')
    # Ajout de filtres par date de création
    list_filter = ('created_at',)
    # Trier les objets par ordre décroissant de création
    ordering = ('-created_at',)
    # Nombre d'éléments affichés par page
    list_per_page = 20
    # Champs affichés dans le formulaire de l'admin
    fields = (
        'player_1', 
        'player_2',  
        'match_start_time', 
        'match_end_time', 
        'score_player_1', 
        'score_player_2', 
        'created_at'
    )

    def get_readonly_fields(self, request, obj=None):
        """
        Rend certains champs en lecture seule dans l'interface admin :
        - Lors de l'édition, les champs `created_at`, `player_1`, et `player_2` ne peuvent pas être modifiés.
        - Lors de la création, aucun champ n'est en lecture seule.
        """
        if obj:  # Si on édite un objet existant
            return ['created_at', 'player_1', 'player_2']
        return []




