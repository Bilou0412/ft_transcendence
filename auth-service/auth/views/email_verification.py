from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny 
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import  force_str
from django.utils.http import  urlsafe_base64_decode
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_summary="Verify Email Address",
    operation_description="This view verifies a user's email address using a token and a UID.",
    manual_parameters=[
        openapi.Parameter('uidb64', openapi.IN_PATH, description="Base64 encoded user ID", type=openapi.TYPE_STRING),
        openapi.Parameter('token', openapi.IN_PATH, description="Verification token", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Confirmation message"),
            }
        )),
        202: 'Accepted - The request has been accepted for processing',
        400: 'Bad Request - Invalid verification link',
        403: 'Forbidden - User is not allowed to verify this email',
        410: 'Gone - The verification token has expired or is no longer valid',
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def email_verification(request, uidb64, token):
    """
    View to verify email address.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):
            if user.is_active:
                return Response({"detail": "Email has already been verified."}, status=status.HTTP_410_GONE)

            # Here you could update the user to mark their email as verified
            user.is_active = True  # or other logic to activate the user
            user.save()

            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Invalid verification link."}, status=status.HTTP_403_FORBIDDEN)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response({"detail": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    operation_summary="Confirm Password Reset",
    operation_description="This view allows users to reset their password by providing a new password, along with a valid UID and token received via email.",
    manual_parameters=[
        openapi.Parameter('uidb64', openapi.IN_PATH, description="Base64 encoded user ID", type=openapi.TYPE_STRING),
        openapi.Parameter('token', openapi.IN_PATH, description="Password reset token", type=openapi.TYPE_STRING),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'new_password': openapi.Schema(type=openapi.TYPE_STRING, description="The new password for the user"),
        },
        required=['new_password']
    ),
    responses={
        200: openapi.Response('Success', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description="Success message confirming the password reset"),
            }
        )),
        400: 'Bad Request - Invalid reset link, inactive account, missing password, or invalid/expired token',
        500: 'Internal Server Error - An error occurred while processing the request',
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_confirm(request, uidb64, token):
    """
    View to confirm and process password reset.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if not user.is_active:
            return Response(
                {"detail": "This account is inactive"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid or expired reset token"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        new_password = request.data.get('new_password')
        if not new_password:
            return Response(
                {"detail": "New password is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response(
            {"detail": "Password has been reset successfully"}, 
            status=status.HTTP_200_OK
        )
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"detail": "Invalid reset link"}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"detail": "An error occurred while resetting your password"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
