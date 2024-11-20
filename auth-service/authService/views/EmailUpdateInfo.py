from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models import User 


@api_view(['GET'])
@permission_classes([AllowAny])
def EmailUpdateInfo(request, uidb64, token):
    """
    View to verify and update the new email address.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(User, pk=uid)

        if user.new_email and default_token_generator.check_token(user, token):
            # Apply the new email
            user.email = user.new_email
            user.new_email = None  # Clear the temporary field
            user.save()

            return Response(
                {"detail": "Your email address has been verified and updated."},
                status=status.HTTP_200_OK
            )

        return Response(
            {"detail": "Invalid or expired verification link."},
            status=status.HTTP_400_BAD_REQUEST
        )

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"detail": "Invalid verification link."},
            status=status.HTTP_400_BAD_REQUEST
        )
