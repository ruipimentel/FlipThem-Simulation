from genetic_algorithms.GeneticAlgorithm import GeneticAlgorithm
from strategies.server_strategies.exponential import Exponential
from tournament import TOURNAMENT_TYPE


ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'genetic_algorithms/deterministic/data/exponential/1_resource/temp/'
}

ga = GeneticAlgorithm(ga_properties=ga_properties)

ga.read_from_file(29)

print(ga.def_strategy_population_average)

ga.plot()