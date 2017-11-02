from genetic_algorithms.deterministic.deterministic_GA import DeterministicGeneticAlgorithm
from strategies.server_strategies.exponential import Exponential

tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.3
}

# TODO still don't actually use this mutation rate

ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'deterministic/data/exponential/1_resource/temp'
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

ga = DeterministicGeneticAlgorithm(defenders=defender_ga_properties,
                                   attackers=attacker_ga_properties,
                                   ga_properties=ga_properties,
                                   tournament_properties=tournament_properties)
ga.start(7000)
ga.plot()
