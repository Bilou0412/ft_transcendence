from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import UpdateUserInfoSerializer

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def UpdateUserInfo(request):
    """
    View to update user's email and username.
    """
    serializer = UpdateUserInfoSerializer(instance=request.user, data=request.data, context={'request': request})

    if serializer.is_valid():
        serializer.save()
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "detail": "Information updated successfully."
            },
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
