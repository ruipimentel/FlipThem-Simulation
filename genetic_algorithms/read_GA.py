import cProfile
import re

from genetic_algorithms.GeneticAlgorithm import GeneticAlgorithm


ga_properties = {
    'file_location': 'genetic_algorithms/data/deterministic/1_resource/testing/',
}

ga = GeneticAlgorithm(ga_properties=ga_properties)
# re.compile(ga.read_from_file())
ga.read_from_file()
# cProfile.run('re.compile("ga.read_from_file")')

#
# print("GA Properties:", ga.ga_properties)
# print("Defender GA Properties:", ga.defender_ga_properties)
# print("Attacker GA Properties:", ga.attacker_ga_properties)
# print("Game Properties:", ga.game_properties)
#
ga.plot()