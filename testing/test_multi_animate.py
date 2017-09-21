from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.periodic import Periodic

import game as game
import graphics.multi_player_animate as animate
import system
from strategies.player import Player

player1_properties = {
    'multi_rate': False,
    'default_rate': 0.6,
    'keep_move_until_completed': True
}

player2_properties = {
    'multi_rate': True,
    'rates': (0.8, 1.821, 1.623, 0.987),
    'default_rate': 0.4,
    'keep_move_until_completed': True
}

player3_properties = {
    'multi_rate': True,
    'rates': (1.21, 1.334, 1.212, 1.234),
    'default_rate': 0.4,
    'keep_move_until_completed': True
}

player4_properties = {
    'multi_rate': True,
    'rates': (1.512, 0.879, 1.12, 0.897),
    'default_rate': 0.4,
    'keep_move_until_completed': True
}

game_properties = {
        'threshold': False,
        'time_limit': 15.0
    }

s = system.System(1)
player1 = Player("player 1",  strategies=Periodic(0.9))
player2 = Player("player 2", strategies=Periodic(0.5))

g = game.Game((player1, player2), s, game_properties)
g.play()

animate = animate.Animate()
animate.start(g)
