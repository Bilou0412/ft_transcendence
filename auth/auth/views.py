from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny ,IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken ,UntypedToken, TokenError
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from django.conf import settings
from .serializers import UserSerializer
from .serializers import ChangePasswordSerializer
import logging

logger = logging.getLogger(__name__)

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
        # Try to get user by username first, then by email
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.get(email=username)

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(password):
            return Response(
                {"detail": "Invalid credentials"}, 
                status=status.HTTP_400_BAD_REQUEST
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
        })

    except User.DoesNotExist:
        return Response(
            {"detail": "Invalid credentials"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error in token view: {str(e)}")
        return Response(
            {"detail": "An error occurred during authentication"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
            # Ici, tu pourrais mettre à jour l'utilisateur pour marquer son email comme vérifié
            user.is_active = True  # ou une autre logique pour activer l'utilisateur
            user.save()

            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

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
            logger.error(f"Error in signup view: {str(e)}")
            return Response(
                {"detail": "An error occurred during registration"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
        logger.error(f"Error in refresh_token view: {str(e)}")
        return Response(
            {"detail": "Invalid or expired refresh token"}, 
            status=status.HTTP_400_BAD_REQUEST
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
        logger.error(f"Error in reset_password_request view: {str(e)}")
        return Response(
            {"detail": "An error occurred while processing your request"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        logger.error(f"Error in reset_password_confirm view: {str(e)}")
        return Response(
            {"detail": "An error occurred while resetting your password"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    View to log out the user by revoking the refresh token.
    """
    try:
        # Récupérer le jeton de rafraîchissement de la requête
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Supprimer le jeton de rafraîchissement
        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response({"detail": "Déconnexion réussie"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        logger.error(f"Error in logout view: {str(e)}")
        return Response({"detail": "An error occurred during logout"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_token(request):
    """
    View to validate a JWT token.
    """
    token = request.data.get('token')

    if not token:
        return Response({"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        UntypedToken(token)  # Vérifie si le token est valide
        return Response({"detail": "Token is valid"}, status=status.HTTP_200_OK)
    except TokenError:
        return Response({"detail": "Token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
