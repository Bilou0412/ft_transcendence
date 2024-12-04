from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random

class Player:
	def __init__ (self, id):
		# self.id = id
		self.pos = {'x': 0, 'y': 0}
		self.score = 0
		self.direction = 0

	def move (self):
		self.pos['y'] += self.direction
		if self.pos['y'] > 15:
			self.pos['y'] = 15
		if self.pos['y'] < -15:
			self.pos['y'] = -15

class Ball:
	def __init__ (self):
		self.pos = {'x': 0, 'y': 0}
		self.velocity = 2
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

	def add_player (self, player):
		self.players.append(player)

	def remove_player (self, role):
		self.end()
		self.players.pop(role)

	async def start (self):
		print(f'len players: {len(self.players)}')
		if len(self.players) != 2:
			return
		self.status = True
		self.reset()
		await get_channel_layer().group_send(
			self.group_name, {'type': 'assign_role'}
		)
		await get_channel_layer().group_send(
			self.group_name, {'type': 'start_game'}
		)

	async def end (self):
		self.status = False
		if self.players[0].score == 10 or self.players[1].score == 10:
			winner = 'left' if self.players[0].score == 10 else 'right'
		else:
			winner = 'unfinished'
		await get_channel_layer().group_send(
			self.group_name, {
				'type': 'game_ended',
				'data': {
					'winner': winner
				}
			}
		)

	async def send_update(self):
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

	def reset (self):
		self.ball.pos = {'x': 0, 'y': 0}
		self.ball.direction = {'x': random.choice([-0.1, 0.1]), 'y': random.choice([-0.1, 0.1])}
		self.players[0].pos = {'x': -10, 'y': 0}
		self.players[1].pos = {'x': 10, 'y': 0}

	async def update (self):
		try:
			if (len(self.players) != 2):
				self.end()
			self.ball.move()
			self.players[0].move()
			self.players[1].move()
			paddle1 = self.players[0].pos
			paddle2 = self.players[1].pos
			
			# walls collision 
			if self.ball.pos['y'] <= -15 or self.ball.pos['y'] >= 15:
				self.ball.direction['y'] *= -1

			# paddles collision
			if self.ball.pos['x'] <= paddle1['x'] + 1 and \
				self.ball.pos['y'] <= paddle1['y'] + 3 and \
				self.ball.pos['y'] >= paddle1['y'] - 3 or \
				self.ball.pos['x'] >= paddle2['x'] - 1 and \
				self.ball.pos['y'] <= paddle2['y'] + 3 and \
				self.ball.pos['y'] >= paddle2['y'] - 3 :
				self.ball.direction['x'] *= -1

			# score
			if self.ball.pos['x'] <= paddle1['x'] - 1:
				self.players[1].score += 1
				self.reset()
			if self.ball.pos['x'] >= paddle2['x'] + 1:
				self.players[0].score += 1
				self.reset()
			
			self.players[0].direction = 0
			self.players[1].direction = 0

			await self.send_update()

			# print(f'scores update: left: {self.players[0].score}, right: {self.players[1].score}')
			if self.players[0].score == 10 or self.players[1].score == 10:
				self.end()
		
			# self.reset()
		except Exception as e:
			print(f'Error: {str(e)}')