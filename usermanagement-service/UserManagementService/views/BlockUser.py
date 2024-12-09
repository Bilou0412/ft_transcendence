from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import UserProfile ,BlockedUser
from ..decorators import authorize_user




@api_view(['POST'])
@authorize_user
def BlockUser(request):
    """
    Permet à un utilisateur de bloquer un autre utilisateur.
    """
    data = request.data
    required_fields = ['user_to_block']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return Response({
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }, status=status.HTTP_400_BAD_REQUEST)

    user_id = request.id
    user_to_block_id = data['user_to_block']

    # Empêcher le blocage de soi-même
    if user_id == user_to_block_id:
        return Response({
            "error": "You cannot block yourself."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Récupérer les profils utilisateur
        blocker_profile, _ = UserProfile.objects.get_or_create(user_id=user_id)
        blocked_profile, _ = UserProfile.objects.get_or_create(user_id=user_to_block_id)

        # Vérifier si le blocage existe déjà
        block, created = BlockedUser.objects.get_or_create(
            blocker=blocker_profile,
            blocked=blocked_profile
        )

        if not created:
            return Response({
                "message": f"User {user_to_block_id} is already blocked."
            }, status=status.HTTP_200_OK)

        return Response({
            "message": f"User {user_to_block_id} has been blocked successfully."
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "error": f"An unexpected error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
