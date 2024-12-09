from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import json
import uuid

class InviteConsumer(AsyncWebsocketConsumer):
	# ...existing code...

	async def receive(self, text_data):
		data = json.loads(text_data)
		if data['type'] == 'invite_to_game':
			await self.invite_to_game(data['sender_id'], data['opponent_id'])

	async def invite_to_game(self, sender_id, opponent_id):
		invite_key = str(uuid.uuid4())
		cache.set(invite_key, {'inviter': sender_id, 'opponent': opponent_id})
		await self.channel_layer.group_send(
			self.lobby_group_name,
			{
				'type': 'game_invitation',
				'invite_key': invite_key,
				'inviter': sender_id,
				'opponent': opponent_id
			}
		)

	async def game_invitation(self, event):
		invite_key = event['invite_key']
		inviter = event['inviter']
		opponent = event['opponent']
		if self.userId in [inviter, opponent]:
			await self.send(text_data=json.dumps({
				'type': 'game_invitation',
				'invite_key': invite_key,
				'inviter': inviter,
				'opponent': opponent
			}))
