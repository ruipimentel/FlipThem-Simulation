from genetic_algorithms.genetic_algorithm import GeneticAlgorithm


ga_properties = {
    'file_location': 'genetic_algorithms/data/deterministic/1_resource/periodic/larger_bounds/',
}

ga = GeneticAlgorithm(ga_properties=ga_properties)
ga.read_from_file()

#
print("GA Properties:", ga.ga_properties)
print("Tournament Properties", ga.tournament_properties)
print("Defender GA Properties:", ga.defender_ga_properties)
print("Attacker GA Properties:", ga.attacker_ga_properties)

# ga.run(5000, 20)

ga.plot()
# ga.plot_strategy_count()
# ga.plot_variance_stats()


