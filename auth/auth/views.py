from rest_framework.decorators import api_view
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
        user = get_object_or_404(User, email=request.data['username']) or User.objects.get(username=request.data['username'])
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
