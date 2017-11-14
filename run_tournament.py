from tournament import Tournament
from tournament import TOURNAMENT_TYPE
from strategies.player import  Player
from strategies.server_strategies.exponential import Exponential

from genetic_algorithms.GeneticAlgorithm import GeneticAlgorithm


defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.4,)
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.4,)
}


game_properties = {
    'time_limit': 1000
}

tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.3,
    'tournament_type': TOURNAMENT_TYPE.DETERMINISTIC,
    'game_properties': game_properties
}



ga = GeneticAlgorithm()
defenders = ga.generate_players(defender_ga_properties, 3)
attackers = ga.generate_players(attacker_ga_properties, 3)

t = Tournament(defender_strategies=defenders,
                           attacker_strategies=attackers,
                           tournament_properties=tournament_properties)

t.play_tournament()

