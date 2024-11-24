from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Match
from django.shortcuts import get_object_or_404

@api_view(['POST'])
def EndMatch(request):
    """
    Cette vue permet de terminer un match. Elle vérifie si les deux joueurs ont confirmé la fin du match.
    """
    match_id = request.data.get('match_id')
    player_id = request.data.get('player_id')  # L'id du joueur qui confirme la fin

    if not match_id or not player_id:
        return Response({"error": "Match ID and Player ID are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Récupérer le match par ID
    match = get_object_or_404(Match, id=match_id)

    if match.status != 'active':
        return Response({"error": "Match is not active."}, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier quel joueur confirme la fin du match et mettre à jour son champ de confirmation
    if match.player_1.id == player_id:
        match.confirmed_by_player_1 = True
    elif match.player_2 and match.player_2.id == player_id:
        match.confirmed_by_player_2 = True
    else:
        return Response({"error": "Player not part of the match."}, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier si les deux joueurs ont confirmé la fin du match
    if match.confirmed_by_player_1 and match.confirmed_by_player_2:
        # Les deux joueurs ont confirmé la fin du match
        match.status = 'completed'
        match.save()

        # Enregistrer les scores et la durée dans la base de données (si nécessaire)
        score_player_1 = request.data.get('score_player_1')
        score_player_2 = request.data.get('score_player_2')
        duration = request.data.get('duration')

        if score_player_1 is not None and score_player_2 is not None and duration is not None:
            match.score_player_1 = score_player_1
            match.score_player_2 = score_player_2
            match.duration = duration
            match.save()

        return Response({
            "message": "Match successfully ended and recorded.",
            "match_id": match.id,
            "score_player_1": match.score_player_1,
            "score_player_2": match.score_player_2,
            "duration": match.duration,
        }, status=status.HTTP_200_OK)
    
    return Response({
        "message": "Waiting for the other player to confirm the end of the match."
    }, status=status.HTTP_200_OK)
