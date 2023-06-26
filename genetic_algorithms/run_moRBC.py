from genetic_algorithms.multiobjective_random_bit_climber import MultiobjectiveRandomBitClimber
from strategies.server_strategies.exponential import Exponential
from strategies.player import Player
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.lm_periodic import LastMove
from strategies.server_strategies.phase_periodic import PhasePeriodic
from core.tournament import TOURNAMENT_TYPE
from copy import copy
import numpy as np

game_properties = {'time_limit': 200}

tournament_properties = {
    'number_of_rounds': 5,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 1,
    'tournament_type': TOURNAMENT_TYPE.STOCHASTIC,  # STOCHASTIC = as computer simulation.
    'game_properties': game_properties,
}

ea_properties = {
    'file_location': 'data/moRBC/stochastic/1_resource/non_fixed/equilibrium/case_1/',
    'upper_bound': 3.0,
    'lower_bound': 0.1,
    'print_out': False
}

defender_ea_properties = {
    'rate_bitstring_length': 7,
    'name': "Defender ",
    'number_of_players': 1,
    'strategy_classes': (Periodic,),
    'move_costs': (0.2,),
    # 'move_costs': (0.2, 0.15, 0.12,),
}
# #
attacker_ea_properties = {
    'rate_bitstring_length': 7,
    'name': "Attacker ",
    'number_of_players': 1,
    'strategy_classes': (Periodic,),
    'move_costs': (0.3,),
    # 'move_costs': (0.18, 0.13, 0.09,),
}
#
# fixed_attacker_properties = {'move_costs': (0.2,),
#                              }

#
# middle_rate = 1.667
# std = 0.0
# attacker_list = []
#
# for i in range(0, 1):
#     rate = middle_rate * (1 + np.random.uniform(-std,std))
#     attacker_list.append(Player(name="Fixed Attacker " + str(i),
#                                 strategies=(Periodic(rate),),
#                                 player_properties=copy(fixed_attacker_properties)))


# attacker_list = tuple(attacker_list)

morbc = MultiobjectiveRandomBitClimber(
    defenders=defender_ea_properties,
    attackers=attacker_ea_properties,
    ea_properties=ea_properties,
    tournament_properties=tournament_properties,
)


morbc.run(1000, 50)
morbc.plot()
# morbc.plot()

# morbc.plot_variance_stats()
