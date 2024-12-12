import os
from rest_framework.decorators import api_view
from ..decorators import authorize_user
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
from django.contrib.auth.models import User
from ..models import UserProfileImage
from django.core.exceptions import ObjectDoesNotExist

@api_view(['GET'])
@authorize_user
def ImageServe(request, id):
    try:
        try:
            user = User.objects.get(id=id)
        except ObjectDoesNotExist:
            default_path = os.path.join('images', 'default.png')
            if os.path.exists(default_path):
                return FileResponse(open(default_path, 'rb'))
            return Response(
                {'error': 'Image file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        profile_image = UserProfileImage.objects.get(user=user)
        image_path = profile_image.image.path
        if not os.path.exists(image_path):
            return Response(
                {'error': 'Image file not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        content_type = None
        if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif image_path.lower().endswith('.png'):
            content_type = 'image/png'
        elif image_path.lower().endswith('.gif'):
            content_type = 'image/gif'

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
