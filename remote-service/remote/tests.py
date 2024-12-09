import unittest
from .models import Game, Player

class TestGame(unittest.TestCase):

    def setUp(self):
        self.game = Game('oui')
        self.ball = self.game.ball
        self.left_paddle = Player(1)
        self.right_paddle = Player(0)
        self.game.players = [self.left_paddle, self.right_paddle]

    def test_ball_collides_with_left_side_of_paddle(self):
        self.ball.pos = {'x': 1, 'y': 5}
        self.left_paddle.pos = {'x': 2, 'y': 5}
        self.left_paddle.dimension = {'w': 2, 'h': 10}
        self.game.handle_collision(self.left_paddle)
        self.assertEqual(self.ball.pos['x'], 0.5)
        self.assertEqual(self.ball.direction['x'], -1)

    def test_ball_collides_with_right_side_of_paddle(self):
        self.ball.pos = {'x': 3, 'y': 5}
        self.right_paddle.pos = {'x': 2, 'y': 5}
        self.right_paddle.dimension = {'w': 2, 'h': 10}
        self.game.handle_collision(self.right_paddle)
        self.assertEqual(self.ball.pos['x'], 3.5)
        self.assertEqual(self.ball.direction['x'], -1)

    def test_ball_collides_with_top_side_of_paddle(self):
        self.ball.pos = {'x': 2, 'y': 4}
        self.left_paddle.pos = {'x': 2, 'y': 5}
        self.left_paddle.dimension = {'w': 2, 'h': 2}
        self.game.handle_collision(self.left_paddle)
        self.assertEqual(self.ball.pos['y'], 3.5)
        self.assertEqual(self.ball.direction['y'], -1)

    def test_ball_collides_with_bottom_side_of_paddle(self):
        self.ball.pos = {'x': 2, 'y': 6}
        self.left_paddle.pos = {'x': 2, 'y': 5}
        self.left_paddle.dimension = {'w': 2, 'h': 2}
        self.game.handle_collision(self.left_paddle)
        self.assertEqual(self.ball.pos['y'], 6.5)
        self.assertEqual(self.ball.direction['y'], -1)

    def test_ball_does_not_collide_with_paddle(self):
        self.ball.pos = {'x': 10, 'y': 10}
        self.left_paddle.pos = {'x': 2, 'y': 5}
        self.left_paddle.dimension = {'w': 2, 'h': 10}
        self.game.handle_collision(self.left_paddle)
        self.assertEqual(self.ball.pos['x'], 10)
        self.assertEqual(self.ball.pos['y'], 10)

if __name__ == '__main__':
    unittest.main()