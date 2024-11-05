import os
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models import UserProfileImage

@api_view(['DELETE'])
def	ImageDelete(request):
    token = request.headers.get('Authorization', '')
    if not token:
        return Response({'error': 'No token'}, status=status.HTTP_401_UNAUTHORIZED)
    response = requests.post('http://alias:8000/api/auth/token/validate/', headers={'Authorization': token})
    if response.status_code != 200:
        return Response({'error': 'Invalid token', 'status': response.status_code}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = User.objects.get(username=response.json()['username'])
    os.remove(UserProfileImage.objects.get(user=user).image.path)
    UserProfileImage.objects.get(user=user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)