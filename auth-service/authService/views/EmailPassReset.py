from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from ..serializers import PassResetConfirmSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def PassResetConfirm(request, uidb64, token):
    """
    View to confirm and process password reset.
    """
    serializer = PassResetConfirmSerializer(data={**request.data, "uidb64": uidb64, "token": token})
    
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"detail": "Password has been reset successfully"}, 
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
