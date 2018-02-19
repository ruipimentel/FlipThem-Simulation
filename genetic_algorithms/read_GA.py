from genetic_algorithms.genetic_algorithm import GeneticAlgorithm


ga_properties = {
    'file_location': 'genetic_algorithms/data/thesis/stochastic/1_resource/non_fixed/equilibrium/case_1/',
}

# data/deterministic/1_resource/periodic/larger_bounds/take_three
# data/stochastic/3_resource/2_threshold/periodic/0203/take_one/'
# genetic_algorithms/data/deterministic/1_resource/periodic/larger_bounds/take_three

ga = GeneticAlgorithm(ga_properties=ga_properties)
ga.read_from_file()

#
print("GA Properties:", ga.ga_properties)
print("Tournament Properties", ga.tournament_properties)
print("Defender GA Properties:", ga.defender_ga_properties)
print("Attacker GA Properties:", ga.attacker_ga_properties)

# ga.ga_properties['print_out'] = True

# ga.run(200, 10)

ga.plot()
# ga.plot_strategy_count(100)
# ga.plot_variance_stats()


