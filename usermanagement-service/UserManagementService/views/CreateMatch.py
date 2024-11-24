from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from ..models import Match, UserProfile
from ..decorators import authorize_user

@api_view(['POST'])
@authorize_user
def CreateMatch(request):
    """
    Crée un match ou confirme un match existant.
    - Si le créateur (player_1) fait la requête : crée un nouveau match
    - Si l'invité (player_2) fait la requête : confirme le match existant
    """
    authenticated_user_id = request.id  # ID de l'utilisateur qui fait la requête
    other_player_id = request.data.get('player_id')  # ID de l'autre joueur

    if not other_player_id:
        return Response({
            "error": "Missing player_id in request"
        }, status=status.HTTP_400_BAD_REQUEST)

    if authenticated_user_id == other_player_id:
        return Response({
            "error": "Cannot create a match with yourself"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Vérifier et créer les profils utilisateurs si nécessaire
    try:
        player_1_profile, _ = UserProfile.objects.get_or_create(user_id=authenticated_user_id)
        player_2_profile, _ = UserProfile.objects.get_or_create(user_id=other_player_id)
    except Exception as e:
        return Response({
            "error": f"Failed to retrieve or create user profiles: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Chercher un match existant entre ces deux joueurs
    existing_match = Match.objects.filter(
        (Q(player_1=player_1_profile) & Q(player_2=player_2_profile)) |
        (Q(player_1=player_2_profile) & Q(player_2=player_1_profile)),
        status__in=['pending', 'active']
    ).first()

    # Cas où l'utilisateur authentifié est player_2 (confirmation de match)
    if existing_match and existing_match.player_2 == player_1_profile:
        if existing_match.status == 'pending':
            existing_match.status = 'active'
            existing_match.match_start_time = timezone.now()
            existing_match.save()
            
            return Response({
                "message": "Match confirmed and started",
                "match_id": existing_match.id,
                "player_1_id": existing_match.player_1.user_id,
                "player_2_id": existing_match.player_2.user_id,
                "status": existing_match.status,
                "start_time": existing_match.match_start_time
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Match is already active or cancelled"
            }, status=status.HTTP_400_BAD_REQUEST)

    # Cas où l'utilisateur authentifié est player_1 (création de match)
    if existing_match:
        return Response({
            "error": "A match already exists between these players"
        }, status=status.HTTP_400_BAD_REQUEST)

    # Créer un nouveau match
    try:
        match = Match.objects.create(
            player_1=player_1_profile,  # Créateur est toujours player_1
            player_2=player_2_profile,
            status='pending'
        )
        
        return Response({
            "message": "Match created successfully. Waiting for player 2 to confirm.",
            "match_id": match.id,
            "player_1_id": match.player_1.user_id,
            "player_2_id": match.player_2.user_id,
            "status": match.status
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "error": f"Failed to create match: {str(e)}"
        }, status=status.HTTP_400_BAD_REQUEST)
