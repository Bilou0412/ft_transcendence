import json
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Game, Player
import asyncio

host, port = settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]
REDIS_URL = f"redis://{host}:{port}"

games = {}
games_loop_task = None
games_lock = asyncio.Lock()

async def games_loop():
	while True:
		for game in games.values():
			# print(f'game: {game.group_name} || status: {game.status}')
			if game.status:
				# print(f'active: {game.group_name}')
				await game.update()
		await asyncio.sleep(0.016)  # Adjust the sleep time as needed

class PongConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		global games_loop_task
		# print(dir(self))
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.group_name = f'pong_{self.room_name}'
		print(f"Connecting to group: {self.group_name}")

		await self.channel_layer.group_add(
			self.group_name,
			self.channel_name
		)
		await self.accept()

		async with games_lock:
			if self.group_name not in games:
				games[self.group_name] = Game(self.group_name)
				self.role = 0
			else :
				self.role = 1
			
			if games_loop_task is None:
				games_loop_task = asyncio.create_task(games_loop())
				print("Started games loop task")

			await games[self.group_name].add_player(Player(self.role))

	async def disconnect(self, close_code):
		async with games_lock:
		# print(f'Disconnecting from group: {self.group_name}')
		# if self.group_name in games:
			tmp = len(games[self.group_name].players)
			await games[self.group_name].remove_player(self.role)
			print(f'my_name: {self.role} ||len before remove: {tmp} || len after remove: {len(games[self.group_name].players)}')

			await games[self.group_name].end()
			if len(games[self.group_name].players) == 0:
				del games[self.group_name]
				print(f"Deleted game: {self.group_name}")



			await self.channel_layer.group_discard(
				self.group_name,self.channel_name)


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
		# print(f'self.role: {self.role} || Paddle moved: {data}')
		
		if games[self.group_name].status == False:
			return

		game = games[self.group_name]
		direction = data['direction']
		game.players[self.role].direction += 0.5 if direction == 'up' else -0.5

	async def handle_start_game(self, data):
		print(f'game started: {self.group_name}')
		await games[self.group_name].start()

	async def handle_end_game(self, data):
		await self.channel_layer.group_send(
			self.group_name,
			{
				'type': 'game_ended',
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

	async def start_game(self, event):
		await self.send(text_data=json.dumps({
			'event': 'start_game',
			# 'data': event['data']
		}))

	async def player_disconnected(self, event):
		if self.role == 1:
			self.role = 0
		# await self.assign_role(event)

	async def assign_role(self, event):
		await self.send(text_data=json.dumps({
			'event': 'assign_role',
			'data': 'left' if self.role == 0 else 'right'
		}))

	async def game_ended(self, event):
		await self.send(text_data=json.dumps({
			'event': 'game_ended',
			'data': event['data']
		}))

	async def game_update(self, event):
		await self.send(text_data=json.dumps({
			'event': 'game_update',
			'data': event['data']
		}))

	async def game_reset(self, event):
		await self.send(text_data=json.dumps({
			'event': 'game_reset',
			'data': event['data']
		}))

	async def unknown_event(self, event):
		await self.send(text_data=json.dumps({
			'event': 'unknown_event',
			'data': event['data']
		}))
