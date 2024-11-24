from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Match,MatchHistory
from ..decorators import authorize_user

@api_view(['POST'])
@authorize_user
def EndMatch(request):
    """
    Cette vue permet de terminer un match et de mettre à jour l'historique du match.
    """
    match_id = request.data.get('match_id')
    score_player_1 = request.data.get('score_player_1')
    score_player_2 = request.data.get('score_player_2')
    duration = request.data.get('duration')  # La durée en secondes

    if not all([match_id, score_player_1, score_player_2, duration]):
        return Response({"error": "Missing required data."}, status=status.HTTP_400_BAD_REQUEST)

    # Récupérer le match par ID
    match = Match.objects.filter(id=match_id, status='active').first()

    if not match:
        return Response({"error": "Match not found or not active."}, status=status.HTTP_404_NOT_FOUND)

    # Créer une entrée dans MatchHistory
    match_history = MatchHistory.objects.create(
        player_1=match.player_1,
        player_2=match.player_2,
        score_player_1=score_player_1,
        score_player_2=score_player_2,
        duration=duration
    )

    # Mettre à jour les scores et la durée dans MatchHistory
    match_history.save()

    # Mettre à jour l'historique des deux joueurs
    match.status = 'completed'  # Le match est maintenant terminé
    match.save()

    return Response({
        "message": "Match ended and recorded in history.",
        "match_id": match.id,
        "score_player_1": score_player_1,
        "score_player_2": score_player_2,
        "duration": duration
    }, status=status.HTTP_200_OK)