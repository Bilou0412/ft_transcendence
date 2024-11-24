from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import MatchHistory
from ..decorators import authorize_user

@api_view(['GET'])
@authorize_user
def MatchHistory(request):
    """
    Récupérer l'historique des matchs de l'utilisateur.
    """
    try:
        matches = MatchHistory.objects.filter(player_1__user_id=request.id) | MatchHistory.objects.filter(player_2__user_id=request.id)
        match_data = [{"date_of_match": match.date_of_match, "score_player_1": match.score_player_1, "score_player_2": match.score_player_2} for match in matches]
        return Response(match_data)
    except Exception as e:
        return Response({"message": str(e)}, status=400)