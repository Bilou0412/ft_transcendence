from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_type = self.scope['url_route']['kwargs']['chat_type']
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.chat_group_name = f'{self.chat_type}_{self.chat_id}'
        self.user = self.scope["user"]

        await self.channel_layer.group_add(
            self.chat_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.chat_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # data = json.loads(text_data)
        # message = data['message']
        message = text_data

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

# from channels.generic.websocket import AsyncWebsocketConsumer
# import json
# from .models import ChatRoom, Message
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.chat_type = self.scope['url_route']['kwargs']['chat_type']
#         self.chat_id = self.scope['url_route']['kwargs']['chat_id']
#         self.chat_group_name = f'{self.chat_type}_{self.chat_id}'
#         self.user = self.scope["user"]

#         self.room = await self.get_room()
#         if not self.room:
#             await self.close()
#             return
#         await self.channel_layer.group_add(
#             self.chat_group_name,
#             self.channel_name
#         )
#         await self.accept()

#     async def disconnect(self, close_code):
#         # Leave chat group
#         await self.channel_layer.group_discard(
#             self.chat_group_name,
#             self.channel_name
#         )

#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         message = text_data
#         # text_data_json = json.loads(text_data)
#         # message = text_data_json['message']
#         # command = text_data_json['command']

#         # Process command and save message to the database
#         # await self.process_command(command)
#         new_message = await self.save_message(message, self.user, self.room)

#         # Send message to chat group
#         await self.channel_layer.group_send(
#             self.chat_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': new_message.content,
#                 # 'sender': new_message.sender.username,
#                 'timestamp': str(new_message.timestamp)
#             }
#         )

#     # Receive message from group
#     async def chat_message(self, event):
#         message = event['message']
#         sender = event['sender']
#         timestamp = event['timestamp']

#         # Send message to WebSocket
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'sender': sender,
#             'timestamp': timestamp
#         }))

#     # Fetch room based on chat_type and chat_id
#     async def get_room(self):
#         try:
#             if self.chat_type == 'game':
#                 return await ChatRoom.objects.aget(name=self.chat_group_name)
#             elif self.chat_type == 'tournament':
#                 return await ChatRoom.objects.aget(name=self.chat_group_name)
#             else:
#                 return None
#         except ChatRoom.DoesNotExist:
#             return None


#     async def save_message(self, content, sender, room):
#         message = await Message.objects.acreate(
#             room=room,
#             sender=sender,
#             content=content
#         )
#         return message