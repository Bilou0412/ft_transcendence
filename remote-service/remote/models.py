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
		self.velocity = 0.5
		self.direction = {'x': 0.1, 'y': 0.1}
	
	def move (self):
		self.pos['x'] += self.velocity * self.direction
		self.pos['y'] += self.velocity * self.direction
	
	def predict_move(self):
		return {
			'x': self.pos['x'] + self.velocity * self.direction['x'],
			'y': self.pos['y'] + self.velocity * self.direction['y']
		}


class Game:
	def __init__ (self, name):
		self.time = 0
		self.ball = Ball()
		self.players = []
		self.status = False

	def add_player (self, player):
		self.players.append(player)

	def remove_player (self, index):
		self.players.pop(index)

	def start (self):
		if len(self.players) == 2:
			self.status = True

	def end (self):
		self.status = False

	def reset (self):
		self.ball.pos = {'x': 0, 'y': 0}
		self.ball.direction = {'x': 0.1, 'y': 0.1}
		self.players[0].pos = {'x': -10, 'y': 0}
		self.players[1].pos = {'x': 10, 'y': 0}

	def update (self):
		new_move = self.ball.predict_move()
		self.players[0].move()
		self.players[1].move()

		paddle1 = self.players[0].pos
		paddle2 = self.players[1].pos
		
		if new_move['y'] <= -10 or new_move['y'] >= 10:
			self.ball.direction['y'] *= -1
		if new_move['x'] <= paddle1['x'] + 0.5 and \
			new_move['y'] <= paddle1['y'] + 2.5 and \
			new_move['y'] >= paddle1['y'] - 2.5 or \
			new_move['x'] >= paddle2['x'] - 0.5 and \
			new_move['y'] <= paddle2['y'] + 2.5 and \
			new_move['y'] >= paddle2['y'] - 2.5 :
			self.ball.direction['x'] *= -1

		if new_move['x'] < self.players[0].pos['x']:
			self.players[1].score += 1
			self.reset()
		if new_move['x'] > self.players[1].pos['x']:
			self.players[0].score += 1
			self.reset()