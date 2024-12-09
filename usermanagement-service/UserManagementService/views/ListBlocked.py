from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import BlockedUser, UserProfile
from ..decorators import authorize_user

@api_view(['GET'])
@authorize_user
def ListBlocked(request):
    """
    Récupérer la liste des utilisateurs bloqués par l'utilisateur.
    """
    try:
        user_profile = UserProfile.objects.get(user_id=request.id)
        blocked_users = BlockedUser.objects.filter(blocker=user_profile)
        blocked = [blocked_user.blocked.user_id for blocked_user in blocked_users]
        return Response({ "user_id": request.id, "blocked_users": blocked })
    except UserProfile.DoesNotExist:
        return Response({"message": "User not found"}, status=404)
