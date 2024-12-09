from channels.generic.websocket import AsyncWebsocketConsumer
import json
from ..models import UserInfo
from ..decorators import auth_token
# from . import connected_users
from django.core.cache import cache

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
		# connected_users[self.userId] = UserInfo(id=self.userId, username=self.username)

	@auth_token
	async def disconnect(self, close_code):
		# connected_users.pop(self.userId, None)
		cache.delete(self.userId)
		await self.channel_layer.group_discard(
			self.lobby_group_name,
			self.channel_name
		)