from tournament import Tournament
from system import System
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.exponential import Exponential
from strategies.player import Player
from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
from genetic_algorithms import GeneticAlgorithm

#
# TODO: Better Ranking system
# TODO: Decide on mutation
# TODO: Generalise to allow any strategy
# TODO: Clean up the shitty code
# We are keeping the keep rate constant at 50% for now

example_tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 3,
    'defender_threshold': 1,
}
example_game_properties = {
    'time_limit': 100.0
}
# TODO still don't actually use this
example_ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'data/'
}

# What about instead of players updating their populations "simultaneously", the defender finds the best response
# to the current attacker population, then the attacker responds to that defenders population
# So on and so forth.



class GeneticAlgorithm(GeneticAlgorithm):

    def start(self, number_of_rounds):

        for s in range(0, len(self.defenders[0].get_strategies())):
            self.def_strategy_population_average[s] = []
            self.att_strategy_population_average[s] = []

        for i in range(0, number_of_rounds):
            print("------ Round " + str(i + 1) + " --------")

            for d in range(0, 10):
                # Here the defender updates his rates

                # Play tournament
                if i > 0:
                    self.system = System(self.system.get_number_of_servers())
                t = Tournament(defender_strategies=self.defenders, attacker_strategies=self.attackers,
                               system=self.system, game_properties=example_game_properties,
                               tournament_properties=self.tournament_properties)

                t.play_tournament()

                # Organise the results
                defender_results = list(t.get_mean_defense().items())

                attacker_results = list(t.get_mean_attack().items())

                sorted_defender_results = sorted(defender_results, key=lambda tup: tup[1], reverse=True)
                sorted_attacker_results = sorted(attacker_results, key=lambda tup: tup[1], reverse=True)

                for s in range(0, len(self.defenders[0].get_strategies())):
                    self.def_strategy_population_average[s].append(np.mean([x[0].get_strategy_rate(s)
                                                                   for x in sorted_defender_results[0:self.def_keep_number]]))

                for s in range(0, len(self.attackers[0].get_strategies())):
                    self.att_strategy_population_average[s].append(np.mean([x[0].get_strategy_rate(s)
                                                                   for x in sorted_attacker_results[0:self.att_keep_number]]))

                self.def_benefit_average.append(np.mean([x[1] for x in sorted_defender_results[0:self.def_keep_number]]))
                self.att_benefit_average.append(np.mean([x[1] for x in sorted_attacker_results[0:self.att_keep_number]]))

                self.def_benefit_average_average.append(np.mean(self.def_benefit_average))
                self.att_benefit_average_average.append(np.mean(self.att_benefit_average))

                ################################################################################
                #                                                                              #
                #                              PRINTING                                        #
                #                                                                              #
                ################################################################################

                print("----- Defender update: ", d, " of round:", i)
                for r in sorted_defender_results:
                    rates = []
                    for strategy in r[0].get_strategies():
                        rates.append(str(strategy))
                    print(r[0].get_name(), rates, r[1])

                print("-------------------")

                for r in sorted_attacker_results:
                    rates = []
                    for strategy in r[0].get_strategies():
                        rates.append(str(strategy))
                    print(r[0].get_name(), rates, r[1])

                #########################################################
                #                                                       #
                #                  Genetic Algorithm                    #
                #                                                       #
                #########################################################

                if len(self.defenders) > 1:
                    self.create_new_generation(sorted_defender_results, self.def_keep_number, i)

            for a in range(0, 10):
                # Here the attacker updates his rates

                # Play tournament
                if i > 0:
                    self.system = System(self.system.get_number_of_servers())
                t = Tournament(defender_strategies=self.defenders, attacker_strategies=self.attackers,
                               system=self.system, game_properties=example_game_properties,
                               tournament_properties=self.tournament_properties)

                t.play_tournament()

                # Organise the results
                defender_results = list(t.get_mean_defense().items())

                attacker_results = list(t.get_mean_attack().items())

                sorted_defender_results = sorted(defender_results, key=lambda tup: tup[1], reverse=True)
                sorted_attacker_results = sorted(attacker_results, key=lambda tup: tup[1], reverse=True)

                for s in range(0, len(self.defenders[0].get_strategies())):
                    self.def_strategy_population_average[s].append(np.mean([x[0].get_strategy_rate(s)
                                                                            for x in sorted_defender_results[
                                                                                     0:self.def_keep_number]]))

                for s in range(0, len(self.attackers[0].get_strategies())):
                    self.att_strategy_population_average[s].append(np.mean([x[0].get_strategy_rate(s)
                                                                            for x in sorted_attacker_results[
                                                                                     0:self.att_keep_number]]))

                self.def_benefit_average.append(
                    np.mean([x[1] for x in sorted_defender_results[0:self.def_keep_number]]))
                self.att_benefit_average.append(
                    np.mean([x[1] for x in sorted_attacker_results[0:self.att_keep_number]]))

                self.def_benefit_average_average.append(np.mean(self.def_benefit_average))
                self.att_benefit_average_average.append(np.mean(self.att_benefit_average))

                ################################################################################
                #                                                                              #
                #                              PRINTING                                        #
                #                                                                              #
                ################################################################################

                print("----- Attacker update: ", a, " of round", i)
                for r in sorted_defender_results:
                    rates = []
                    for strategy in r[0].get_strategies():
                        rates.append(str(strategy))
                    print(r[0].get_name(), rates, r[1])

                print("-------------------")

                for r in sorted_attacker_results:
                    rates = []
                    for strategy in r[0].get_strategies():
                        rates.append(str(strategy))
                    print(r[0].get_name(), rates, r[1])

                    #########################################################
                    #                                                       #
                    #                  Genetic Algorithm                    #
                    #                                                       #
                    #########################################################


                if len(self.attackers) > 1:
                    self.create_new_generation(sorted_attacker_results, self.att_keep_number, i)



tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.5
}

game_properties = {
    'time_limit': 1000.0
}

# TODO still don't actually use this mutation rate

ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'data/flipit/vary_both/'
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Periodic,),
    'move_costs': (1.0, ),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Periodic,),
    'move_costs': (3.0, ),
}

attacker_properties = {'move_costs': attacker_ga_properties['move_costs']}
defender_properties = {'move_costs': defender_ga_properties['move_costs']}

single_attacker = (Player("Attacker ", player_properties=copy(attacker_properties), strategies=(Periodic(0.055), )),)
single_defender = (Player("Defender ", player_properties=copy(defender_properties), strategies=(Periodic(0.166), )),)

ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      system=System(1),
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties,
                      game_properties=game_properties)
ga.start(100)
ga.plot()
#
# for i in range(0, 30):
#
#     genetic_algorithms = GeneticAlgorithm(defender_ga_properties, attacker_ga_properties, System(1), ga_properties,
#                           tournament_properties, game_properties)
#
#     genetic_algorithms.start(500)
#
#     genetic_algorithms.write_to_file(i)
# # # #
# # #
# genetic_algorithms = GeneticAlgorithm(ga_properties=ga_properties)
# genetic_algorithms.read_from_file()
# genetic_algorithms.plot()
#
#
# plot_universes(ga_properties['file_location'], 30)
