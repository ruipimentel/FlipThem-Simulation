from genetic_algorithms.GeneticAlgorithm import GeneticAlgorithm
from strategies.server_strategies.exponential import Exponential
from tournament import TOURNAMENT_TYPE

game_properties = {'time_limit': 1000}

tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.3,
    'tournament_type': TOURNAMENT_TYPE.STOCHASTIC,
    'game_properties': game_properties
}

# TODO still don't actually use this mutation rate

ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'stochastic/data/exponential/1_resource/defender04attacker04/'
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.4,),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.4,),
}

ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties)
ga.start(10000, 100)
ga.plot()

#
# /Users/chrissherfield/Documents/Python/flipitlibrary/genetic_algorithms
#
#
# /Users/chrissherfield/Documents/Python/flipitlibrary