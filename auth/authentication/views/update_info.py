from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated ,AllowAny
from rest_framework.response import Response
from ..models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.conf import settings
from ..serializers import UpdateInfo
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework.response import Response  # Correct import
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    """
    View to update user's email and username.
    """
    user = request.user
    data = request.data

    # Serialize the user data
    serializer = UpdateInfo(user, data=data)
    if user.Student == True:
        return Response({"detail": "Vous n'êtes pas autorisé à modifier vos informations."}, status=status.HTTP_400_BAD_REQUEST)
    if serializer.is_valid():
        # Check if email or username changed
        email_changed = data.get('email') and data.get('email') != user.email
        username_changed = data.get('username') and data.get('username') != user.username

        if email_changed:
            # Store the new email temporarily for verification
            user.new_email = data.get('email')
            user.save()

            # Generate the token and verification URL for the new email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = request.build_absolute_uri(
                reverse('update_email_verification', kwargs={'uidb64': uid, 'token': token})
            )

            # Send the email verification message
            send_mail(
                subject="Vérification de votre nouvelle adresse e-mail",
                message=f'Veuillez cliquer sur le lien suivant pour vérifier votre nouvelle adresse e-mail : {verification_url}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.new_email],
                fail_silently=False,
            )

            return Response({
                "detail": "Un e-mail de vérification a été envoyé à votre nouvelle adresse email."
            }, status=status.HTTP_200_OK)
        if username_changed:
            user.username = data.get('username')
            user.save()
        # If only username changed, or no significant changes, return success
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
        }, status=status.HTTP_200_OK)

    # If serializer is not valid, return errors
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_new_email(request, uidb64, token):
    """
    View to verify the new email address.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)

        if default_token_generator.check_token(user, token) and user.new_email:
            # Appliquer le nouvel email
            user.email = user.new_email
            user.new_email = None  # Nettoyer le champ temporaire
            user.save()

            return Response({"detail": "Votre adresse e-mail a été vérifiée et mise à jour."}, status=status.HTTP_200_OK)

        else:
            return Response({"detail": "Lien de vérification invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"detail": "Lien de vérification invalide."}, status=status.HTTP_400_BAD_REQUEST)