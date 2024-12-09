from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import UserProfile
from ..decorators import authorize_user

@api_view(['GET'])
@authorize_user
def UserStats(request):
    """
    Récupérer les statistiques de l'utilisateur : nombre de jeux, victoires, défaites et durée moyenne.
    """
    try:
        user_profile = UserProfile.objects.get(user_id=request.id)
        return Response({
            'user_id': user_profile.user_id,
            'nb_game': user_profile.nb_game,
            'nb_win': user_profile.nb_win,
            'nb_losses': user_profile.nb_losses,
            'avg_duration': user_profile.avg_duration
        })
    except UserProfile.DoesNotExist:
        return Response({"message": "User profile not found"}, status=404)