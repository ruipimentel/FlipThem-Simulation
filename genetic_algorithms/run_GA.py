from genetic_algorithms.GeneticAlgorithm import GeneticAlgorithm
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.lm_periodic import LastMovePeriodic
from strategies.server_strategies.phase_periodic import PhasePeriodic
from tournament import TOURNAMENT_TYPE

game_properties = {'time_limit': 1000}

tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.3,
    'tournament_type': TOURNAMENT_TYPE.DETERMINISTIC,
    'game_properties': game_properties
}

# TODO still don't actually use this mutation rate

ga_properties = {
    'mutation_rate': 0.01,
    'file_location': 'data/deterministic/1_resource/profiling/',
    'print_out': False
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.4,)
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential, ),
    'move_costs': (0.4,)
}

ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties)
ga.run(100, 20)
ga.plot()
