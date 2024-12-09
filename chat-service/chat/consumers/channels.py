from channels.generic.websocket import AsyncWebsocketConsumer
import json
from ..decorators import auth_token
from django.core.cache import cache

class ChatConsumer(AsyncWebsocketConsumer):
    @auth_token
    async def connect(self):
        self.chatType = self.scope['url_route']['kwargs']['chat_type']
        self.chatId = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = 'error'

        if self.chatType == 'game':
            self.chat_group_name = f'{self.chatType}_{self.chatId}'
        elif self.chatType == 'direct':
            self.newDMConnection()
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid chat type'
            }))
            return
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        
        await self.accept()

    @auth_token
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']


        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender
        }))

    async def newDMConnection(self):
        if self.userId == int(self.chatId):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid chat id'
            }))
            return
        if not cache.get(self.chatId):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'User not connected'
            }))
            return
        participants = sorted([self.userId, int(self.chatId)])
        self.chat_group_name = f'{self.chatType}_{participants[0]}_{participants[1]}'

