import os
import requests
from rest_framework.decorators import api_view
from ..decorators import authorize_user
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models import UserProfileImage
from django.core.exceptions import ObjectDoesNotExist

@api_view(['DELETE'])
@authorize_user
def	ImageDelete(request):
    username = getattr(request, 'username')
    try:
        user = User.objects.get(username=username)
        profileImage = UserProfileImage.objects.get(user=user)
        
        if not os.path.exists(profileImage.image.path):
            return Response(
                {'error': 'imag not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        os.remove(profileImage.image.path)
        profileImage.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    except ObjectDoesNotExist:
        return Response(
            {'error': 'User does not exists'},
            status=status.HTTP_404_NOT_FOUND
        )

    except UserProfileImage.DoesNotExist:
        return Response(
            {'error': 'image not found'},
            status=status.HTTP_404_NOT_FOUND
        )