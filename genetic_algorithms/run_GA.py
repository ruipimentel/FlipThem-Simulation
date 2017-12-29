from genetic_algorithms.genetic_algorithm import GeneticAlgorithm
from strategies.server_strategies.exponential import Exponential
from strategies.player import Player
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.lm_periodic import LastMove
from strategies.server_strategies.phase_periodic import PhasePeriodic
from tournament import TOURNAMENT_TYPE

game_properties = {'time_limit': 200}

tournament_properties = {
    'number_of_rounds': 5,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.3,
    'tournament_type': TOURNAMENT_TYPE.DETERMINISTIC,
    'game_properties': game_properties,
}

ga_properties = {
    'mutation_rate': 0.002,
    'file_location': 'data/deterministic/1_resource/periodic/larger_bounds/',
    'upper_bound': 5.0,
    'print_out': False
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Periodic,),
    # 'move_costs': (0.2, 0.3, 0.1)
    'move_costs': (0.2,),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Periodic,),
    # 'move_costs': (0.1, 0.2, 0.3),
    'move_costs': (0.2,),
}

ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties)


ga.run(5000, 10)
ga.plot()
# ga.plot()

# ga.plot_variance_stats()
