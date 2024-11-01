from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
import requests
import os
from ..models import UserProfileImage

@api_view(['GET'])
def ImageServe(request, username):
    """
    Serve profile image for a specific user by their username.
    """
    try:
        # Validate token with auth service
        token = request.headers.get('Authorization', '')
        if token:
            response = requests.post(
                'http://alias:8000/api/auth/token/validate/',
                headers={'Authorization': token}
            )
            if response.status_code != 200:
                return Response(
                    {'error': 'Invalid token', 'status': response.status_code},
                    status=status.HTTP_401_UNAUTHORIZED
                )

        # Get the user and their profile image
        user = get_object_or_404(User, username=username)
        profile_image = UserProfileImage.objects.filter(user=user).first()

        if not profile_image or not profile_image.image:
            # If no image exists, serve default image
            default_path = os.path.join('media', 'default-profile.png')
            if os.path.exists(default_path):
                return FileResponse(open(default_path, 'rb'))
            return Response(
                {'error': 'No profile image found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the actual image file
        image_path = profile_image.image.path
        if not os.path.exists(image_path):
            return Response(
                {'error': 'Image file not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Determine content type
        content_type = None
        if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif image_path.lower().endswith('.png'):
            content_type = 'image/png'
        elif image_path.lower().endswith('.gif'):
            content_type = 'image/gif'

        # Serve the file
        response = FileResponse(open(image_path, 'rb'))
        if content_type:
            response['Content-Type'] = content_type
        response['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour

        return response

    except Exception as e:
        return Response(
            {'error': 'An error occurred', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
