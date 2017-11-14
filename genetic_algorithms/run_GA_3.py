from genetic_algorithms.GeneticAlgorithm import GeneticAlgorithm
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.periodic import Periodic
from tournament import TOURNAMENT_TYPE

game_properties = {'time_limit': 1000}


tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 3,
    'defender_threshold': 1,
    'selection_ratio': 0.3,
    'tournament_type': TOURNAMENT_TYPE.DETERMINISTIC,
    'game_properties': game_properties
}


ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'data/deterministic/mixed/1_resource/'
}


defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential, Periodic),
    'move_costs': (0.3, 0.38, 0.45,),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential, Periodic),
    'move_costs': (0.15, 0.12, 0.23),
}

ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties)

ga.start(10000, 100)
