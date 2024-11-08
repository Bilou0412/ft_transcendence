from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny ,IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.conf import settings
from ..serializers import UserSerializer
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken ,BlacklistedToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_summary="Obtain JWT Token",
    operation_description="This view allows users to obtain a JWT token pair by providing a username or email and a password.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username or email of the user"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="Password of the user"),
        },
        required=['username', 'password']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
                'access': openapi.Schema(type=openapi.TYPE_STRING, description="Access token"),
                'user': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID"),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                    }
                ),
            }
        )),
        400: 'Bad Request - Both username/email and password are required',
        401: 'Unauthorized - Invalid username or password',
        403: 'Forbidden - This account is inactive',
        404: 'Not Found - User not found',
        500: 'Internal Server Error - An error occurred during authentication',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    """
    View to obtain JWT token pair for a user.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {"detail": "Both username/email and password are required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.filter(username=username).first() or User.objects.filter(email=username).first()

        if user is None:
            return Response(
                {"detail": "Invalid username or password"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.check_password(password):
            return Response(
                {"detail": "Invalid username or password"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
        }, status=status.HTTP_200_OK)

    except Exception:
        return Response(
            {"detail": "An error occurred during authentication"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='post',
    operation_summary="User Registration",
    operation_description="This view allows users to register by providing a username, email, and password, with password confirmation. An email verification link is sent to the user.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description="The user's username"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="The user's email address"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="The user's password"),
            'password2': openapi.Schema(type=openapi.TYPE_STRING, description="Password confirmation"),
        },
        required=['username', 'email', 'password', 'password2']
    ),
    responses={
        201: openapi.Response('Created', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token"),
                'access': openapi.Schema(type=openapi.TYPE_STRING, description="Access token"),
                'user': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID"),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                    }
                ),
            }
        )),
        400: 'Bad Request - Invalid registration data',
        500: 'Internal Server Error - An error occurred during registration',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    View to register a new user.
    """
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Construire l'URL de vérification
            verification_url = request.build_absolute_uri(
                reverse('email_verification', kwargs={'uidb64': uid, 'token': token})
            )

            # Envoyer l'email de vérification
            send_mail(
                subject="Vérification de votre adresse e-mail",
                message=f'Veuillez cliquer sur le lien suivant pour vérifier votre adresse e-mail : {verification_url}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"detail": "An error occurred during registration"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    operation_summary="Logout",
    operation_description="This view allows authenticated users to log out by blacklisting their refresh token.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="The refresh token to be blacklisted"),
        },
        required=['refresh']
    ),
    responses={
        205: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Success message confirming the logout"),
            }
        )),
        400: 'Bad Request - Refresh token is required or already blacklisted/invalid',
        401: 'Unauthorized - User is not authenticated',
        500: 'Internal Server Error - An error occurred during logout',
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        # Obtenez le refresh token de la requête
        refresh_token = request.data.get('refresh')

        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Obtenez l'objet OutstandingToken
        outstanding_token = OutstandingToken.objects.get(token=refresh_token)

        # Vérifiez si le token est déjà blacklisté
        if BlacklistedToken.objects.filter(token=outstanding_token).exists():
            return Response({"detail": "Token already blacklisted or invalid."}, status=status.HTTP_400_BAD_REQUEST)

        # Blacklistez le token
        BlacklistedToken.objects.create(token=outstanding_token)

        return Response({"detail": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)

    except OutstandingToken.DoesNotExist:
        return Response({"detail": "Token already blacklisted or invalid."}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"detail": "An error occurred during logout."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)