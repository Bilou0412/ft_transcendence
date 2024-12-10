from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
import json


@api_view(['POST'])
def friend_request(request):
    try:
        data = request.data
        receiver_id = data.get('receiver_id')
        sender_id = data.get('sender_id')

        # Validation de la requête
        if not receiver_id or not sender_id:
            return Response({'error': 'Inviter ID and Invitee ID are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtenir le layer de canal pour envoyer un message à la connexion WebSocket
        channel_layer = get_channel_layer()

        # Envoie d'une demande via WebSocket (envoie un message au groupe WebSocket de l'utilisateur invité)
        channel_layer.group_send(
            f"user_{receiver_id}",  # Groupe unique pour chaque utilisateur connecté
            {
                'type': 'friend_request',
                'receiver_id': receiver_id,
                'sender_id': sender_id,
            }
        )
        return Response({'message': 'Friend request sent successfully!'}, status=status.HTTP_200_OK)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON format'}, status=status.HTTP_400_BAD_REQUEST)
