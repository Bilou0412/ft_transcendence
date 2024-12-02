import json
import aioredis
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Game, Player

host, port = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
REDIS_URL = f"redis://{host}:{port}"

games = {}

class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.group_name = f'pong_{self.room_name}'
		print(f"Connecting to group: {self.group_name}")

		await self.channel_layer.group_add(
			self.group_name,
			self.channel_name
		)
		await self.accept()

		if self.group_name not in games:
			games[self.group_name] = Game(self.group_name)
			self.role = 0
			# games[self.group_name].add_player(Player(self.role))
		else :
			self.role = 1
		games[self.group_name].add_player(Player(self.role))

		# client_count = await self.get_client_count()
		# if client_count >= 2:
		# 	await self.close()
		# 	return
		
		# await self.increment_client_count()

		# if not client_count:
		# 	self.role = 1
		# else:
		# 	self.role = 2
		# await self.send(json.dumps({
		# 	'event': 'assign_role',
		# 	'data': f'player{self.role}'
		# }))
		# if self.role == 2:
		# 	await self.channel_layer.group_send(
		# 		self.group_name,{'type': 'game_started'})

	async def disconnect(self, close_code):
		games[self.group_name].remove_player(self.role)
		games[self.group_name].end()
		if len(games[self.group_name].players) == 0:
			del games[self.group_name]

		await self.channel_layer.group_send(
			self.group_name,{'type': 'game_ended'})
		await self.channel_layer.group_send(
			self.group_name,{'type': 'player_disconnected'})

		await self.channel_layer.group_discard(
			self.group_name,self.channel_name)
		
		# await self.decrement_client_count()

	async def receive(self, text_data):
		try:
			text_data_json = json.loads(text_data)
			event = text_data_json['event']
			data = text_data_json['data']

			# Handle different types of events
			if event == 'paddle_moved':
				await self.handle_paddle_moved(data)
			elif event == 'start_game':
				await self.handle_start_game(data)
			elif event == 'end_game':
				await self.handle_end_game(data)
			elif event == 'score_update':
				await self.handle_score_update(data)
			else:
				await self.handle_unknown_event(event, data)
		except json.JSONDecodeError:
			await self.send_error('Invalid JSON')
		except KeyError as e:
			await self.send_error(f'Missing key: {str(e)}')
		except Exception as e:
			await self.send_error(f'Error: {str(e)}')

	async def handle_paddle_moved(self, data):
		print(f'Paddle moved: {data}')
		await self.channel_layer.group_send(
			self.group_name,
			{
				'type': 'paddle_moved',
				'data': data
			}
		)

	async def handle_start_game(self, data):
		await self.channel_layer.group_send(
			self.group_name,
			{
				'type': 'game_started',
			}
		)

	async def handle_end_game(self, data):
		await self.channel_layer.group_send(
			self.group_name,
			{
				'type': 'game_ended',
				# 'data': data
			}
		)

	async def handle_score_update(self, data):
		await self.channel_layer.group_send(
			self.group_name,
			{
				'type': 'score_updated',
				'data': data
			}
		)

	async def handle_unknown_event(self, event, data):
		await self.channel_layer.group_send(
			self.group_name,
			{
				'type': 'unknown_event',
				'data': {'event': event, 'data': data}
			}
		)

	async def send_error(self, message):
		await self.send(text_data=json.dumps({
			'event': 'error',
			'data': {'message': message}
		}))

	async def paddle_moved(self, event):
		await self.send(text_data=json.dumps({
			'event': 'paddle_moved',
			'data': event['data']
		}))

	async def game_started(self, event):
		await self.send(text_data=json.dumps({
			'event': 'game_started',
		}))

	# async def player_disconnected(self, event):
	# 	if self.role == 2:
	# 		self.role = 1
	# 	await self.send(json.dumps({
	# 		'event': 'assign_role',
	# 		'data': f'player{self.role}'
	# 	}))

	async def game_ended(self, event):
		await self.send(text_data=json.dumps({
			'event': 'game_ended',
			# 'data': event['data']
		}))

	async def score_updated(self, event):
		await self.send(text_data=json.dumps({
			'event': 'score_updated',
			'data': event['data']
		}))

	async def unknown_event(self, event):
		await self.send(text_data=json.dumps({
			'event': 'unknown_event',
			'data': event['data']
		}))

	# async def increment_client_count(self):
	# 	redis = await aioredis.from_url(REDIS_URL)
	# 	key = f"group:{self.group_name}:count"
	# 	new_count = await redis.incr(key)
	# 	print(f"Incremented client count for {key}: {new_count}")
	# 	await redis.close()

	# async def decrement_client_count(self):
	# 	redis = await aioredis.from_url(REDIS_URL)
	# 	key = f"group:{self.group_name}:count"
	# 	count = await redis.decr(key)
	# 	print(f"Decremented client count for {key}: {count}")
	# 	if count <= 0:
	# 	    # Clean up Redis key if no clients remain
	# 		await redis.delete(key)
	# 		print(f"Deleted Redis key for {key} as count is {count}")
	# 	await redis.close()

	# async def get_client_count(self):
	# 	# print(f'url: {REDIS_URL}')
	# 	redis = await aioredis.from_url(REDIS_URL)
	# 	key = f"group:{self.group_name}:count"
	# 	count = await redis.get(key)
	# 	print(f"Current client count for {key}: {count}")
	# 	await redis.close()
	# 	return int(count) if count else 0
