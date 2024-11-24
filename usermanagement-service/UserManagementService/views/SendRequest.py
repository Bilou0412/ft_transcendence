from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Friendship, UserProfile
from ..decorators import authorize_user

@api_view(['POST'])
@authorize_user
def SendRequest(request):
    """
    Envoi d'une demande d'amitié.
    """
    try:
        user_1 = UserProfile.objects.get(user_id=request.id)
        user_2 = UserProfile.objects.get(user_id=request.data['friend_user_id'])
        friendship = Friendship.objects.create(user_1=user_1, user_2=user_2, status='pending')
        friendship.save()
        return Response({"message": "Friend request sent"})
    except UserProfile.DoesNotExist:
        return Response({"message": "User not found"}, status=404)