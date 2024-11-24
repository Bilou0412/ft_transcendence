from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Friendship, UserProfile
from ..decorators import authorize_user

@api_view(['GET'])
@authorize_user
def ListFriends(request):
    """
    Récupérer la liste des amis de l'utilisateur.
    """
    try:
        user_profile = UserProfile.objects.get(user_id=request.id)
        friendships = Friendship.objects.filter(user_1=user_profile) | Friendship.objects.filter(user_2=user_profile)
        friends = []
        for friendship in friendships:
            if friendship.status == 'accepted':
                friend = friendship.user_1 if friendship.user_2 == user_profile else friendship.user_2
                friends.append(friend.user_id)
        return Response(friends)
    except UserProfile.DoesNotExist:
        return Response({"message": "User not found"}, status=404)