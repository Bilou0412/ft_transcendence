from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Match
from ..decorators import authorize_user

@api_view(['POST'])
@authorize_user
def CreateMatch(request):
    """
    Crée un match si aucun match n'existe entre les deux joueurs. Si un match existe,
    et qu'il est en attente (`pending`), le joueur 2 peut valider ce match.
    """
    # Récupérer le token du joueur et son ID
    player_1_id = request.id  # L'ID du joueur 1 extrait du token
    player_2_id = request.data.get('player_2_id')  # L'ID du joueur 2 envoyé dans la requête
    
    # Vérifier si l'ID du joueur 2 a été envoyé
    if not player_2_id:
        return Response({"error": "Missing player 2 ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Chercher un match existant entre les deux joueurs
    match = Match.objects.filter(
        (Q(player_1_id=player_1_id) & Q(player_2_id=player_2_id)) |
        (Q(player_1_id=player_2_id) & Q(player_2_id=player_1_id))
    ).first()

    # Si aucun match n'existe, on en crée un (création par le joueur 1)
    if not match:
        # Créer un match avec le statut 'pending'
        match = Match.objects.create(player_1_id=player_1_id, player_2_id=player_2_id, status='pending')
        return Response({
            "message": "Match created successfully. Waiting for the other player to validate.",
            "match_id": match.id,
            "player_1_id": match.player_1_id,
            "player_2_id": match.player_2_id
        }, status=status.HTTP_201_CREATED)

    # Si un match existe, vérifier s'il est en statut 'pending'
    if match.status == 'pending':
        # Vérifier si la requête vient du joueur 2
        if request.id == player_2_id:
            # Mettre à jour le statut du match en 'active'
            match.status = 'active'
            match.save()
            return Response({
                "message": "Match validated successfully.",
                "match_id": match.id,
                "player_1_id": match.player_1_id,
                "player_2_id": match.player_2_id
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Only player 2 can validate the match."}, status=status.HTTP_403_FORBIDDEN)

    # Si le match est déjà validé ou annulé, on retourne une erreur
    return Response({"error": "Match already validated or cancelled."}, status=status.HTTP_400_BAD_REQUEST)
