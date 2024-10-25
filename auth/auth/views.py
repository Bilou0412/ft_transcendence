
from rest_framework.decorators import api_view, permission_classes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny
from django.urls import reverse
from django.conf import settings
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


@api_view(['POST'])
def token(request):
    try:
        user = User.objects.get(username=request.data['username'])
    except User.DoesNotExist:
        user = get_object_or_404(User, email=request.data['username']) or User.objects.get(
            username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {
            "username": user.username,
            "email": user.email,
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def refresh_token(request):
    # Récupère le token de rafraîchissement depuis les données
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({"detail": "Refresh token missing."}, status=400)
    try:
        # Crée un nouvel objet RefreshToken pour valider le token
        refresh = RefreshToken(refresh_token)
        # Génère un nouveau token d'accès
        new_access_token = refresh.access_token
        return Response({
            "access": str(new_access_token),
        }, status=200)
    except TokenError:
        return Response({"detail": "Invalid or expired refresh token."}, status=400)


@api_view(['POST'])
# Pas besoin d'être authentifié pour réinitialiser son mot de passe
@permission_classes([AllowAny])
def reset_password_request_view(request):
    email = request.data.get('email')

    if not email:
        print("Email requis")
        return Response({"error": "Email requis"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "Aucun utilisateur trouvé avec cet email"}, status=status.HTTP_404_NOT_FOUND)

    # Génération du token et de l'UID
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Générer l'URL de réinitialisation du mot de passe
    reset_url = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={
                'uidb64': uid, 'token': token})
    )

    # Envoyer l'e-mail avec le lien de réinitialisation
    send_mail(
        subject="Réinitialisation du mot de passe",
        message=f'Cliquez sur le lien suivant pour réinitialiser votre mot de passe : {reset_url}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user.email],
    )
    return Response({"success": "E-mail de réinitialisation envoyé"}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"error": "Lien invalide"}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)

    new_password = request.data.get('new_password')

    if not new_password:
        return Response({"error": "Mot de passe requis"}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()
    return Response({"success": "Mot de passe réinitialisé avec succès"}, status=status.HTTP_200_OK)
