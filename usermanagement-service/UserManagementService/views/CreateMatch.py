from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Match, UserProfile
from ..decorators import authorize_remote_service
from datetime import datetime

@api_view(['POST'])
def CreateMatch(request):
    """
    Enregistre un match créé et validé par un service distant.
    Accessible uniquement au service de jeu via une clé d'API.
    """
    data = request.data

    # Vérification des données reçues
    required_fields = ['player_1_id', 'player_2_id', 'match_start_time', 'match_end_time', 'score_player_1', 'score_player_2']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return Response({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Extraction des données
    player_1_id = data['player_1_id']
    player_2_id = data['player_2_id']
    match_start_time = data['match_start_time']
    match_end_time = data['match_end_time']
    score_player_1 = data['score_player_1']
    score_player_2 = data['score_player_2']

    # Convertir les dates de type str en objets datetime
    try:
        match_start_time = datetime.fromisoformat(match_start_time.replace("Z", "+00:00"))
        match_end_time = datetime.fromisoformat(match_end_time.replace("Z", "+00:00"))
    except ValueError as e:
        return Response({
            "error": f"Invalid datetime format: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)

    if player_1_id == player_2_id:
        return Response({
            "error": "A match cannot be created between the same player."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier ou créer les profils utilisateur
    try:
        player_1_profile, _ = UserProfile.objects.get_or_create(user_id=player_1_id)
        player_2_profile, _ = UserProfile.objects.get_or_create(user_id=player_2_id)
    except Exception as e:
        return Response({
            "error": f"Failed to retrieve or create user profiles: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Créer un nouveau match
    try:
        match = Match.objects.create(
            player_1=player_1_profile,
            player_2=player_2_profile,
            match_start_time=match_start_time,
            match_end_time=match_end_time,
            score_player_1=score_player_1,
            score_player_2=score_player_2
        )

        # Ajouter le match aux profils des joueurs
        player_1_profile.matches_as_player_1.add(match)
        player_2_profile.matches_as_player_2.add(match)

        # Mise à jour des statistiques des joueurs
        # Calculer la durée du match
        match_duration = (match_end_time - match_start_time).total_seconds()

        # Mise à jour de player_1
        player_1_profile.nb_game += 1
        player_1_profile.avg_duration = ((player_1_profile.avg_duration * (player_1_profile.nb_game - 1)) + match_duration) / player_1_profile.nb_game
        if score_player_1 > score_player_2:
            player_1_profile.nb_win += 1
        else:
            player_1_profile.nb_losses += 1

        # Mise à jour de player_2
        player_2_profile.nb_game += 1
        player_2_profile.avg_duration = ((player_2_profile.avg_duration * (player_2_profile.nb_game - 1)) + match_duration) / player_2_profile.nb_game
        if score_player_2 > score_player_1:
            player_2_profile.nb_win += 1
        else:
            player_2_profile.nb_losses += 1

        # Sauvegarder les profils après mise à jour
        player_1_profile.save()
        player_2_profile.save()

        return Response({
            "message": "Match successfully recorded.",
            "match_id": match.id,
            "player_1_id": match.player_1.user_id,
            "player_2_id": match.player_2.user_id,
            "start_time": match.match_start_time,
            "end_time": match.match_end_time,
            "score_player_1": match.score_player_1,
            "score_player_2": match.score_player_2
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "error": f"Failed to create match: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)

