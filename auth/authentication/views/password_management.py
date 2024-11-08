from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny ,IsAuthenticated
from rest_framework.response import Response
from ..models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.conf import settings
from ..serializers import ChangePasswordSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_summary="Request Password Reset",
    operation_description="This view allows users to request a password reset email by providing their registered email address.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="The user's registered email address"),
        },
        required=['email']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Confirmation message indicating the reset email was sent"),
            }
        )),
        400: 'Bad Request - Email is required or account is inactive',
        500: 'Internal Server Error - An error occurred while processing the request',
    }
)

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_request(request):
    """
    View to request a password reset email.
    """
    email = request.data.get('email')
    
    if not email:
        return Response(
            {"detail": "Email is required"}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        if not user.is_active:
            return Response(
                {"detail": "This account is inactive"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        # Build reset URL
        reset_url = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        # Send email
        send_mail(
            subject="Password Reset Request",
            message=f'Click the following link to reset your password: {reset_url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response(
            {"detail": "Password reset email has been sent"}, 
            status=status.HTTP_200_OK
        )

    except User.DoesNotExist:
        # Return success even if email doesn't exist for security
        return Response(
            {"detail": "Password reset email has been sent"}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"detail": "An error occurred while processing your request"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@swagger_auto_schema(
    method='post',
    operation_summary="Change Password",
    operation_description="This view allows authenticated users to change their password by providing their old and new passwords.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'old_password': openapi.Schema(type=openapi.TYPE_STRING, description="The user's current password"),
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="The new password for the user"),
        },
        required=['old_password', 'new_password']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Success message confirming the password change"),
            }
        )),
        400: 'Bad Request - Invalid old password or validation errors',
        401: 'Unauthorized - User is not authenticated',
        500: 'Internal Server Error - An error occurred while processing the request',
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    View to change the password of the authenticated user.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        # Vérification de l'ancien mot de passe
        if not user.check_password(old_password):
            return Response(
                {"detail": "L'ancien mot de passe est incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Changement de mot de passe
        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Le mot de passe a été changé avec succès."},
            status=status.HTTP_200_OK
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

