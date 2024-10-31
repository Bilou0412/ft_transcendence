# views.py
import requests
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .serializers import UserProfileImageSerializer
from .models import UserProfileImage

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def ImageUpload(request):
    try:
        token = request.headers.get('Authorization', '')
        response = requests.post('http://web_dev/api/auth/token/validate/', headers={'Authorization': token})
        if response.status_code != 200:
            return Response({'error': 'invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        username = request.data.get('username')
        if not username:
            return Response({'error': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user, created = User.objects.get_or_create(username=username, defaults={'is_active': True})
        
        serializer = UserProfileImageSerializer(data=request.data)
        if serializer.is_valid():
            # Check if there's an existing UserProfileImage for this user
            profile_image, created = UserProfileImage.objects.get_or_create(user=user)
            
            # Update the image if it already exists
            profile_image.image = serializer.validated_data['image']
            profile_image.save()
            
            response_serializer = UserProfileImageSerializer(profile_image)
            return Response(
                {
                    'message': 'Image uploadée avec succès',
                    'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'error': 'Données invalides',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {
                'error': 'Une erreur est survenue',
                'details': str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
