from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import pyotp
import qrcode
from io import BytesIO
import base64

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # L'utilisateur doit être authentifié
def enable_2fa(request):
    """
    Génère la clé secrète et le QR code pour l'activation de la 2FA.
    """
    user = request.user

    # Vérifie si la 2FA est déjà activée
    if user.otp_secret:
        return Response(
            {"detail": "2FA is already enabled."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Générer une clé secrète OTP unique
    otp_secret = pyotp.random_base32()
    user.otp_secret = otp_secret
    user.save()

    # URL pour l'application d'authentification
    otp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(
        name=user.email,
        issuer_name="Pongo"
    )

    # Générer le QR code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(otp_uri)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Convertir l'image en base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    # Ne pas inclure `otp_secret` dans la réponse
    return Response({
        "qr_code": qr_code_base64,  # QR code sous forme d'image
        "detail": "Scan this QR code with your 2FA app."
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # L'utilisateur doit être authentifié
def verify_2fa(request):
    """
    Vérifie le code OTP fourni par l'utilisateur et active la 2FA.
    """
    user = request.user
    otp_code = request.data.get("otp")

    if not user.otp_secret:
        return Response(
            {"detail": "2FA has not been initialized for this user."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Vérifier le code OTP
    totp = pyotp.TOTP(user.otp_secret)
    if totp.verify(otp_code):
        # Si le code OTP est valide, la 2FA reste activée (clé déjà définie)
        return Response({"detail": "2FA enabled successfully."}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])  # L'utilisateur doit être authentifié
def disable_2fa(request):
    """
    Désactive la 2FA en supprimant le champ `otp_secret`.
    """
    user = request.user

    if not user.otp_secret:
        return Response(
            {"detail": "2FA is not enabled."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Supprimer le secret OTP
    user.otp_secret = None
    user.save()

    return Response({"detail": "2FA disabled successfully."}, status=status.HTTP_200_OK)
