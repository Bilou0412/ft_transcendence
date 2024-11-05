import os
import requests
from rest_framework.decorators import api_view
from ..decorators import authorize_user
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models import UserProfileImage

@api_view(['DELETE'])
@authorize_user
def	ImageDelete(request):
    username = getattr(request, 'username')
    user = User.objects.get(username=username)
    os.remove(UserProfileImage.objects.get(user=user).image.path)
    UserProfileImage.objects.get(user=user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)