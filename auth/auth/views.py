from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny ,IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.conf import settings
from .serializers import UserSerializer
from .serializers import ChangePasswordSerializer
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
    method='get',
    operation_summary="Verify Email Address",
    operation_description="This view verifies a user's email address using a token and a UID.",
    manual_parameters=[
        openapi.Parameter('uidb64', openapi.IN_PATH, description="Base64 encoded user ID", type=openapi.TYPE_STRING),
        openapi.Parameter('token', openapi.IN_PATH, description="Verification token", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Confirmation message"),
            }
        )),
        202: 'Accepted - The request has been accepted for processing',
        400: 'Bad Request - Invalid verification link',
        403: 'Forbidden - User is not allowed to verify this email',
        410: 'Gone - The verification token has expired or is no longer valid',
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def email_verification(request, uidb64, token):
    """
    View to verify email address.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if user.is_active:
                return Response({"detail": "Email has already been verified."}, status=status.HTTP_410_GONE)

            # Here you could update the user to mark their email as verified
            user.is_active = True  # or other logic to activate the user
            user.save()

            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_403_FORBIDDEN)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

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
    operation_summary="Request Password Reset",
    operation_description="This view allows users to request a password reset email by providing their registered email address.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="The user's registered email address"),
        },
        required=['email']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Confirmation message indicating the reset email was sent"),
            }
        )),
        400: 'Bad Request - Email is required or account is inactive',
        500: 'Internal Server Error - An error occurred while processing the request',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_request(request):
    """
    View to request a password reset email.
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {"detail": "Email is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        if not user.is_active:
            return Response(
                {"detail": "This account is inactive"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset URL
        reset_url = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        # Send email
        send_mail(
            subject="Password Reset Request",
            message=f'Click the following link to reset your password: {reset_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Password reset email has been sent"}, 
            status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        # Return success even if email doesn't exist for security
        return Response(
            {"detail": "Password reset email has been sent"}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"detail": "An error occurred while processing your request"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='post',
    operation_summary="Confirm Password Reset",
    operation_description="This view allows users to reset their password by providing a new password, along with a valid UID and token received via email.",
    manual_parameters=[
        openapi.Parameter('uidb64', openapi.IN_PATH, description="Base64 encoded user ID", type=openapi.TYPE_STRING),
        openapi.Parameter('token', openapi.IN_PATH, description="Password reset token", type=openapi.TYPE_STRING),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="The new password for the user"),
        },
        required=['new_password']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Success message confirming the password reset"),
            }
        )),
        400: 'Bad Request - Invalid reset link, inactive account, missing password, or invalid/expired token',
        500: 'Internal Server Error - An error occurred while processing the request',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request, uidb64, token):
    """
    View to confirm and process password reset.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not user.is_active:
            return Response(
                {"detail": "This account is inactive"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        new_password = request.data.get('new_password')
        if not new_password:
            return Response(
                {"detail": "New password is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password has been reset successfully"}, 
            status=status.HTTP_200_OK
        )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"detail": "Invalid reset link"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"detail": "An error occurred while resetting your password"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='post',
    operation_summary="Change Password",
    operation_description="This view allows authenticated users to change their password by providing their old and new passwords.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING, description="The user's current password"),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="The new password for the user"),
        },
        required=['old_password', 'new_password']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Success message confirming the password change"),
            }
        )),
        400: 'Bad Request - Invalid old password or validation errors',
        401: 'Unauthorized - User is not authenticated',
        500: 'Internal Server Error - An error occurred while processing the request',
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    View to change the password of the authenticated user.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        # Vérification de l'ancien mot de passe
        if not user.check_password(old_password):
            return Response(
                {"detail": "L'ancien mot de passe est incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Changement de mot de passe
        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Le mot de passe a été changé avec succès."},
            status=status.HTTP_200_OK
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
        return Response({'message': 'token valide.', 'username': user.username}, status=status.HTTP_200_OK)
    return Response({'message': 'token invalide.'}, status=status.HTTP_400_BAD_REQUEST)