from channels.generic.websocket import AsyncWebsocketConsumer
from ..models import UserInfo
from ..decorators import auth_token
# from . import connected_users
from django.core.cache import cache
import json

class LobbyConsumer(AsyncWebsocketConsumer):
	@auth_token
	async def connect(self):
		self.lobby_group_name = 'lobby'
		await self.channel_layer.group_add(
			self.lobby_group_name,
			self.channel_name
		)
		await self.accept()
		cache.set(self.userId, UserInfo(id=self.userId, username=self.username))
		connected_user_ids = cache.get('connected_user_ids', set())
		connected_user_ids.add(self.userId)
		cache.set('connected_user_ids', connected_user_ids)
		connected_users = cache.get_many(connected_user_ids)
		await self.channel_layer.group_send(
			self.lobby_group_name,
			{
				'type': 'list_user_connected',
				'users': [user.username for user in connected_users.values()]
			}
		)

	@auth_token
	async def disconnect(self, close_code):
		cache.delete(self.userId)
		await self.channel_layer.group_discard(
			self.lobby_group_name,
			self.channel_name
		)
		connected_user_ids = cache.get('connected_user_ids', set())
		connected_user_ids.discard(self.userId)
		cache.set('connected_user_ids', connected_user_ids)
		connected_users = cache.get_many(connected_user_ids)
		await self.channel_layer.group_send(
			self.lobby_group_name,
			{
				'type': 'list_user_connected',
				'users': [user.username for user in connected_users.values()]
			}
		)

	async def list_user_connected(self, event):
		users = event['users']
		await self.send(text_data=json.dumps({
			'type': 'list_user_connected',
			'users': users
		}))