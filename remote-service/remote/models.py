from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random
from datetime import datetime

class Player:
	def __init__ (self, id):
		# self.id = id
		self.pos = {'x': 0, 'y': 0}
		self.score = 0
		self.direction = 0

	def move (self):
		self.pos['y'] += self.direction
		if self.pos['y'] > 10:
			self.pos['y'] = 10
		if self.pos['y'] < -10:
			self.pos['y'] = -10

class Ball:
	def __init__ (self):
		self.pos = {'x': 0, 'y': 0}
		self.velocity = 1
		self.direction = {'x': 0.1, 'y': 0.1}
	
	def move (self):
		self.pos['x'] += self.velocity * self.direction['x']
		self.pos['y'] += self.velocity * self.direction['y']


class Game:
	def __init__ (self, group_name):
		self.time = 0
		self.ball = Ball()
		self.players = []
		self.group_name = group_name
		self.status = False
		self.last_update_time = datetime.now()

	def add_player (self, player):
		self.players.append(player)

	def remove_player (self, role):
		print(f'indexxxxxxxxxxxxx: {role}')
		self.players.pop(role)

	async def start (self):
		if len(self.players) == 2:
			self.status = True
		self.reset()
		self.time = datetime.now()
		await get_channel_layer().group_send(
			self.group_name,{'type': 'assign_role'})
		await get_channel_layer().group_send(
			self.group_name, {
				'type': 'game_started',
				'data': {
					'ball': {
						'direction': self.ball.direction,
						'velocity': self.ball.velocity
					}
				# 	'players': {
				# 		'left': {'pos': self.players[0].pos, 'score': self.players[0].score},
				# 		'right': {'pos': self.players[1].pos, 'score': self.players[1].score}
				# 	}

				}
			}
		)

	def end (self):
		self.status = False

	async def reset (self):
		self.ball.pos = {'x': 0, 'y': 0}
		self.ball.direction = {'x': random.choice([-0.1, 0.1]), 'y': random.choice([-0.1, 0.1])}
		self.players[0].pos = {'x': -10, 'y': 0}
		self.players[1].pos = {'x': 10, 'y': 0}
		await get_channel_layer().group_send(
			self.group_name, {
				'type': 'game_reset',
				'data': {
					'ball': {
						'direction': self.ball.direction,
					}
				}})
				# 	'players': {
				# 		'left': {'pos': self.players[0].pos, 'score': self.players[0].score},
				# 		'right': {'pos': self.players[1].pos, 'score': self.players[1].score}
				# 	}

		# 		}
		# 	}
		# )

	async def update (self):
		try:
			# now = datetime.now()
			# delta_time = (now - self.last_update_time).total_seconds()
			# self.last_update_time = now

			self.ball.move()
			self.players[0].move()
			self.players[1].move()
			paddle1 = self.players[0].pos
			paddle2 = self.players[1].pos
			# print(f'ball: {self.ball.pos}')
			if self.ball.pos['y'] <= -10 or self.ball.pos['y'] >= 10:
				self.ball.direction['y'] *= -1
			
			if self.ball.pos['x'] <= paddle1['x'] + 0.5 and \
				self.ball.pos['y'] <= paddle1['y'] + 2.5 and \
				self.ball.pos['y'] >= paddle1['y'] - 2.5 or \
				self.ball.pos['x'] >= paddle2['x'] - 0.5 and \
				self.ball.pos['y'] <= paddle2['y'] + 2.5 and \
				self.ball.pos['y'] >= paddle2['y'] - 2.5 :
				self.ball.direction['x'] *= -1

			if self.ball.pos['x'] < self.players[0].pos['x']:
				self.players[1].score += 1
				self.reset()
			if self.ball.pos['x'] > self.players[1].pos['x']:
				self.players[0].score += 1
				self.reset()

			self.players[0].direction = 0
			self.players[1].direction = 0
			channel = get_channel_layer()
			if channel is None:
				print('channel is none')
			await get_channel_layer().group_send(
				self.group_name, {
					'type': 'game_update',
					'data': {
						'ball': self.ball.pos,
						'players': {
							'left': {'pos': self.players[0].pos, 'score': self.players[0].score},
							'right': {'pos': self.players[1].pos, 'score': self.players[1].score}
						}
					}
				}
			)
		except Exception as e:
			print(f'Error: {str(e)}')