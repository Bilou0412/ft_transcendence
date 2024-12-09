from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import UserProfile, BlockedUser
from ..decorators import authorize_user

@api_view(['POST'])
@authorize_user
def UnblockUser(request):
    """
    Permet à un utilisateur de débloquer un autre utilisateur.
    """
    data = request.data
    required_fields = ['user_to_unblock']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return Response({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.id
    user_to_unblock_id = data['user_to_unblock']

    try:
        # Récupérer les profils utilisateur
        unblocker_profile = UserProfile.objects.get(user_id=user_id)
        unblocked_profile = UserProfile.objects.get(user_id=user_to_unblock_id)

        # Vérifier si le blocage existe
        block = BlockedUser.objects.filter(
            blocker=unblocker_profile,
            blocked=unblocked_profile
        ).first()

        if not block:
            return Response({
                "error": f"User {user_to_unblock_id} is not blocked."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Supprimer le blocage
        block.delete()

        return Response({
            "message": f"User {user_to_unblock_id} has been unblocked successfully."
        }, status=status.HTTP_200_OK)

    except UserProfile.DoesNotExist:
        return Response({
            "error": "User not found."
        }, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({
            "error": f"An unexpected error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
