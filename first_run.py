from core.system import System
# If threshold is false, we assume attackers must get into whole system for benefit and defender has benefit whenever
# they are in control of one or more servers
from graphics.multi_player_animate import Animate
from strategies.player import Player
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.periodic import Periodic
from core.game import Game
from copy import copy



if __name__ == '__main__':
    s = System(1)

    defender_properties = {'move_costs': (0.2,),
                           'threshold': 1
                           }
    attacker_properties = {'move_costs': (0.15,),
                           'threshold': 1
                           }

    defender = Player("Defender ", player_properties=copy(defender_properties),
                      strategies=(Periodic(0.5),))
    attacker = Player("Attacker ",
                      player_properties=copy(attacker_properties),
                      strategies=(Exponential(0.7)))

    game_properties = {'time_limit': 5}

    g = Game(players=(defender, attacker), system=s, game_properties=game_properties)
    g.play()

    g.print_full_game_summary()
    g.print_individual_server_summary()

    a = Animate()
    a.start(g)
