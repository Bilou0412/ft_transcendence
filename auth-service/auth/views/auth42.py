from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
import requests
import os

@api_view(['GET'])
@permission_classes([AllowAny])
def UserCreateFrom42View(request):
    code = request.GET.get('code')
    if not code:
        return Response({"error": "Code not provided"}, status=status.HTTP_400_BAD_REQUEST)

    # Effectuez une requête POST pour obtenir l'access token
    token_url = 'https://api.intra.42.fr/oauth/token'
    try:
        token_response = requests.post(token_url, data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('CLIENT_ID'),
            'client_secret': os.environ.get('CLIENT_SECRET'),
            'code': code,
            'redirect_uri': 'http://127.0.0.1:8000/api/auth/form42/'
        })

        if token_response.status_code != 200:
            return Response({"error": "Failed to obtain access token"}, status=status.HTTP_400_BAD_REQUEST)

        # Récupérez l'access token
        token_data = token_response.json()
        access_token = token_data.get('access_token')

        # Récupérez les informations de l'utilisateur
        user_info_url = 'https://api.intra.42.fr/v2/me'
        user_info_response = requests.get(user_info_url, headers={
            'Authorization': f'Bearer {access_token}'
        })

        if user_info_response.status_code != 200:
            return Response({"error": "Failed to obtain user information"}, status=status.HTTP_400_BAD_REQUEST)

        user_data = user_info_response.json()
        user = User.objects.filter(username=user_data['login']).first()

        if user:
            # L'utilisateur existe, créez les tokens
            tokens = create_tokens_for_user(user)
            return Response({
                "access": tokens['access'],
                "refresh": tokens['refresh'],
                "user":{
                      "id": user.id,
                "username": user.username,
                "email": user.email
                }
            }, status=status.HTTP_200_OK)

        # Créez ou mettez à jour l'utilisateur
        user = create_or_update_user(user_data)

        if not user:
            return Response({"error": "Failed to create or update user"}, status=status.HTTP_400_BAD_REQUEST)

        # Créez les tokens
        tokens = create_tokens_for_user(user)

        # Renvoyez les informations utilisateur et les tokens
        return Response({
            "access": tokens['access'],
            "refresh": tokens['refresh'],
            "id": user.id,
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)

    except requests.RequestException as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_or_update_user(data):
    user, created = User.objects.update_or_create(
        username=data['login'],  # Utilisez le login fourni par l'API 42
        defaults={
            'email': data['email'],
            'is_active': True
        }
    )
    return user

def create_tokens_for_user(user):
    access = AccessToken.for_user(user)
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(access),
        "refresh": str(refresh)
    }
