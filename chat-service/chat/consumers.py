from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import UserInfo
from .decorators import auth_token
import httpx

connected_users = {}

class ChatConsumer(AsyncWebsocketConsumer):
    @auth_token
    async def connect(self):
        self.chatType = self.scope['url_route']['kwargs']['chat_type']
        self.chatId = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'{self.chatType}_{self.chatId}'
    
        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )
        
        blocked = ['jdenis']
        connected_users[self.userId] = UserInfo(id=self.userId, username=self.username, blocked=blocked)

        await self.accept()

    @auth_token
    async def disconnect(self, close_code):
        connected_users.pop(self.userId, None)
        
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

        if sender != self.username and sender in connected_users[self.userId].blocked:
            return

        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'sender': sender
        }))
