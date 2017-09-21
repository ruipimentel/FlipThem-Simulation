import time

from strategies.non_adaptive.exponential import Exponential

import game as game
import system
from strategies.non_adaptive.periodic import Periodic
from strategies.adaptive.lm_periodic import LastMovePeriodic
import graphics.multi_player_animate as animate


base_player_properties = {
    'multi_rate': False,
    'default_rate': 1.0,
    'rates': (),
    'keep_move_until_completed': True,
    'individual_move_costs': True,
    'default_move_costs': 1.0,
    'move_costs': (),
    'threshold': False
}


player1_properties = {
    'multi_rate': True,
    'rates': (0.8, 1.821, 1.623, 0.987),
    'keep_move_until_completed': True,
    'individual_move_costs': True,
    'default_move_costs': 1.0,
    'move_costs': (0.3, 0.4, 0.5, 0.22),
    'threshold': 2
}

s = system.System(2)
periodic_player1 = Periodic("player 1", player1_properties)
periodic_player2 = Periodic("player 2", player1_properties)
# periodic_player3 = Periodic("player 3", player3_properties)
# periodic_player4 = Periodic("player 4", player4_properties)
#

exponential_player_properties = {
    'multi_rate': True,
    'rates': (0.8, 1.821, 1.623, 0.987),
    'keep_move_until_completed': True,
    'individual_move_costs': True,
    'default_move_costs': 1.0,
    'move_costs': (0.3, 0.4, 0.5, 0.22),
    'threshold': 1
}


expPlayer1 = Exponential("Exponential 1", player1_properties)
expPlayer2 = Exponential("Exponential 2", player1_properties)

ad1 = LastMovePeriodic("Adaptive 1", player1_properties)


game_properties = {
        'time_limit': 5.0
}


# Create a game
g = game.Game((ad1, expPlayer1), s, game_properties)

start_time = time.time()
g.play()
# print(time.time() - start_time)
g.print_individual_server_summary()
g.print_full_game_summary()

# print(g.get_system().get_system_reward(player1) + g.get_system().get_system_reward(player2))

# print(g.get_system().get_player_system_reward(player1))
# print(g.get_system().get_system_benefit(player1))
# print(g.get_system().get_system_benefit(player2))

# plt = Plot()
# plt.plot(g.get_system().get_all_servers()[0], expPlayer1, 10, colour='b')
# # plt.plot(g.get_system().get_all_servers()[0], player2, 10, colour='r')
# # plt.plot(g.get_system().get_all_servers()[0], player3, 10, colour='g')
# # #
# plt.show()


# animate = animate.Animate()
# animate.start(g)
