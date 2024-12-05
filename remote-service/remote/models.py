from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import random
from datetime import datetime
import asyncio

class Player:
	def __init__ (self, id):
		# self.id = id
		self.pos = {'x': 0, 'y': 0}
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
		self.score = {'left': 0, 'right': 0}
		self.status = False


	async def add_player (self, player):
			self.players.append(player)

	async def remove_player (self, role):
			if len(self.players) == 0:
				print('Error: No players to remove')
				return
			if role != 0 and role != 1:
				print(f'Error: Invalid role index {role}')
				return
			if role >= len(self.players):
				role = role - 1
			# if role < 0 or role >= len(self.players):
			# 	print(f'Error: Invalid role index {role} for players list of length {len(self.players)}')
			# 	return
			self.players.pop(role)
			
			await self.send_data({'type': 'player_disconnected'})

	async def start (self):
		print(f'len players: {len(self.players)}')
		if len(self.players) != 2:
			return
		self.status = True
		self.reset()
		await self.send_data( {'type': 'assign_role'}
		)
		await self.send_data( {'type': 'start_game'}
		)

	async def end (self):
		print('game ended')
		# time_past = datetime.now() - self.time
		self.status = False
		if self.score['left'] == 10 or self.score['right'] == 10:
			winner = 'left' if self.score['left'] == 10 else 'right'
		else:
			winner = 'unfinished'
		await self.send_data( {
				'type': 'game_ended',
				'data': {
					'winner': winner
				}
			}
		)
		self.score = {'left': 0, 'right': 0}

	async def send_data (self, data):
		await get_channel_layer().group_send(
			self.group_name, data)

	async def send_update(self):
		print('sending update')
		await self.send_data( {
				'type': 'game_update',
				'data': {
					'ball': self.ball.pos,
					'players': {
						'left': {
							'pos': self.players[0].pos,
							'score': self.score['left']},
						'right': {
							'pos': self.players[1].pos,
							'score': self.score['right']},
					}
				}
			}
		)

	def reset (self):
		self.ball.pos = {'x': 0, 'y': 0}
		self.ball.direction = {'x': random.choice([-0.1, 0.1]), 'y': random.choice([-0.1, 0.1])}
		self.players[0].pos = {'x': -10, 'y': 0}
		self.players[1].pos = {'x': 10, 'y': 0}
		# self.score = {'left': 0, 'right': 0}

	async def update (self):
		try:
			self.ball.move()
			self.players[0].move()
			self.players[1].move()

			left_paddle = self.players[0].pos
			right_paddle = self.players[1].pos
			
			# walls collision 
			if self.ball.pos['y'] <= -15 or self.ball.pos['y'] >= 15:
				self.ball.direction['y'] *= -1

			# paddles collision
			if self.ball.pos['x'] <= left_paddle['x'] + 1 and \
				self.ball.pos['y'] <= left_paddle['y'] + 3 and \
				self.ball.pos['y'] >= left_paddle['y'] - 3 or \
				self.ball.pos['x'] >= right_paddle['x'] - 1 and \
				self.ball.pos['y'] <= right_paddle['y'] + 3 and \
				self.ball.pos['y'] >= right_paddle['y'] - 3 :
				self.ball.direction['x'] *= -1

			# score
			if self.ball.pos['x'] <= left_paddle['x'] - 1:
				self.score['left'] += 1
				self.reset()
			if self.ball.pos['x'] >= right_paddle['x'] + 1:
				self.score['right'] += 1
				self.reset()
			
			self.players[0].direction = 0
			self.players[1].direction = 0

			await self.send_update()

			# print(f'scores update: left: {self.players[0].score}, right: {self.players[1].score}')
			if self.score['left'] == 10 or self.score['right'] == 10:
				# print('game ended')
				await self.end()
				self.reset()
		
		except Exception as e:
			print(f'update Error: {str(e)}')