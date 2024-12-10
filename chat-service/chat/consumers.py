from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from .decorators import auth_token
from .models import Conversation, DirectMessage

class ChatConsumer(AsyncWebsocketConsumer):
    @auth_token
    async def connect(self):
        try:
            self.chatId = self.scope['url_route']['kwargs']['chat_id']
            self.chat_group_name = 'error'

            if self.userId == int(self.chatId):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid chat id'
                }))
                await self.close()
                return

            self.participants = sorted([self.userId, int(self.chatId)])
            self.chat_group_name = f'{self.participants[0]}_{self.participants[1]}'
            print(f'self id: {self.userId} chat id: {self.chatId}')
            self.conversation = await self.get_conversation()

            await self.channel_layer.group_add(
                self.chat_group_name,
                self.channel_name
            )
            
            await self.accept()

            # Fetch and send message history
            print('Fetching message history')
            messages = await self.get_message_history(self.conversation)
            print(f'Messages: {messages}')
            await self.send(text_data=json.dumps({
                'type': 'message_history',
                'messages': messages
            }))
        except Exception as e:
            print(f'Error in connect: {e}')
            await self.close()

    @auth_token
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        conversation = await self.get_conversation()
        await self.create_message(conversation, self.username, message)

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


    async def get_conversation(self):
        try:
            conversation, created = await Conversation.objects.aget_or_create(
                participant1=self.participants[0],
                participant2=self.participants[1]
            )
            print(f'Conversation: {conversation}, Created: {created}')
            return conversation
        except Exception as e:
            print(f'Error in get_conversation: {e}')
            raise

    @database_sync_to_async
    def get_message_history(self, conversation):
        try:
            messages = DirectMessage.objects.filter(conversation=conversation).order_by('timestamp')
            return [{'sender': message.sender, 'content': message.content, 'timestamp': message.timestamp.isoformat()} for message in messages]
        except Exception as e:
            print(f'Error in get_message_history: {e}')
            return []


    @database_sync_to_async
    def create_message(self, conversation, sender, content):
        try:
            # conversation = self.get_conversation()
            DirectMessage.objects.create(conversation=conversation, sender=sender, content=content)
        except Exception as e:
            print(f'Error in create_message: {e}')
            raise