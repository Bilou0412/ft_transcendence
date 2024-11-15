from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import  IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_summary="Refresh Access Token",
    operation_description="This view allows users to refresh their access token using a valid refresh token.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="The refresh token required to obtain a new access token"),
        },
        required=['refresh']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'access': openapi.Schema(type=openapi.TYPE_STRING, description="New access token"),
            }
        )),
        400: 'Bad Request - Refresh token is required or invalid',
        500: 'Internal Server Error - An error occurred during token refresh',
    }
)
@api_view(['POST'])
def refresh_token(request):
    """
    View to refresh an access token using a refresh token.
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response(
            {"detail": "Refresh token is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            "access": str(refresh.access_token),
        })
        
    except Exception as e:
        return Response(
            {"detail": "Invalid or expired refresh token"}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@swagger_auto_schema(
    method='post',
    operation_summary="Validate Token",
    operation_description="This view allows users to validate their JWT token and check if they are authenticated.",
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description="Message confirming the token is valid"),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username of the authenticated user"),
            }
        )),
        400: openapi.Response('Invalid Token', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description="Message indicating the token is invalid"),
            }
        )),
        401: 'Unauthorized - User is not authenticated',
    }
)    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    user = request.user 
    if user:
        return Response({'message': 'token valide.', 'id': user.id, 'username': user.username}, status=status.HTTP_200_OK)
    return Response({'message': 'token invalide.'}, status=status.HTTP_400_BAD_REQUEST)