from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..serializers import PassUpdateSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def PassUpdate(request):
    """
    View to change the password of the authenticated user.
    """
    serializer = PassUpdateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"detail": "Password has been update successfully."},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
