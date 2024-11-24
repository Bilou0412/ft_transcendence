from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import Friendship
from ..decorators import authorize_user


@api_view(['POST'])
@authorize_user
def AcceptRequest(request):
    """
    Accepter une demande d'amitié.
    """
    try:
        friendship = Friendship.objects.get(id=request.data['friendship_id'])
        friendship.status = 'accepted'
        friendship.save()
        return Response({"message": "Friendship request accepted"})
    except Friendship.DoesNotExist:
        return Response({"message": "Friendship request not found"}, status=404)