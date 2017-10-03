from deterministic_tournament import DeterministicTournament
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.exponential import Exponential
from strategies.player import Player
from system import System
from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
import os
from GA import GA


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


def defender_equilibrium(costs):
    return costs[1]/(costs[0] + costs[1])**2

def attacker_equilibrium(costs):
    return costs[0]/(costs[0] + costs[1])**2




class GeneticAlgorithm(GA):

    def __init__(self,
                 defenders=None,
                 attackers=None,
                 system=System(1),
                 ga_properties=example_ga_properties,
                 tournament_properties=example_tournament_properties):

        print(system)

        super().__init__(defenders, attackers, system, ga_properties, tournament_properties)

        self.single_population_update = 10

        self.fixed_defender = (Player("Fixed Defender ",
                                      player_properties=copy(defender_properties),
                                      strategies=(Periodic(np.random.uniform(0.0, 0.5)),)),)
        self.fixed_attacker = (Player("Fixed Attacker ",
                                      player_properties=copy(attacker_properties),
                                      strategies=(Periodic(np.random.uniform(0.0, 0.5)),)),)

    def start(self, number_of_rounds):

        for s in range(0, len(self.defenders[0].get_strategies())):
            self.def_strategy_population_average[s] = []
            self.att_strategy_population_average[s] = []

            self.def_strategy_population_average_average[s] = []
            self.att_strategy_population_average_average[s] = []

        for i in range(0, number_of_rounds):
            print("------ Round " + str(i + 1) + " --------")

            for d in range(0, self.single_population_update):
                # Here the defender updates his rates

                t = DeterministicTournament(defender_strategies=self.defenders, attacker_strategies=self.fixed_attacker,
                                            tournament_properties=self.tournament_properties)

                t.play_tournament()

                # Organise the results
                defender_results = list(t.get_mean_defense().items())

                sorted_defender_results = sorted(defender_results, key=lambda tup: tup[1], reverse=True)


                ################################################################################
                #                                                                              #
                #                              PRINTING                                        #
                #                                                                              #
                ################################################################################

                print("----- Defender update: ", d, " of round:", i)
                print("Fixed attacker Strategy: ", self.fixed_attacker[0].get_strategies()[0])
                for r in sorted_defender_results:
                    rates = []
                    for strategy in r[0].get_strategies():
                        rates.append(str(strategy))
                    print(r[0].get_name(), rates, r[1])

                print("-------------------")

                #########################################################
                #                                                       #
                #                  Genetic Algorithm                    #
                #                                                       #
                #########################################################

                if d == self.single_population_update - 1:

                    new_def_strategies = []

                    for s in range(0, len(self.defenders[0].get_strategies())):
                        strategy_average = np.mean([x[0].get_strategy_rate(s)
                                                    for x in sorted_defender_results[0:self.def_keep_number]])

                        self.def_strategy_population_average[s].append(strategy_average)

                        self.def_strategy_population_average_average[s].append(np.mean
                                                                               (self.def_strategy_population_average[s])
                                                                               )
                        if i > 0:
                            new_def_strategies.append(Periodic(self.def_strategy_population_average_average[s][-2]))

                    self.def_benefit_average.append(np.mean([x[1] for x in sorted_defender_results[0:self.def_keep_number]]))

                    self.def_benefit_average_average.append(np.mean(self.def_benefit_average))

                    if i > 0:
                        self.fixed_defender = (Player("Fixed Defender ",
                                               player_properties=copy(defender_properties),
                                               strategies=tuple(new_def_strategies)),)

                else:
                    self.create_new_generation(sorted_defender_results, self.def_keep_number, i)

            for a in range(0, self.single_population_update):
                # Here the attacker updates his rates

                t = DeterministicTournament(defender_strategies=self.fixed_defender, attacker_strategies=self.attackers,
                                            tournament_properties=self.tournament_properties)

                t.play_tournament()

                # Organise the results
                attacker_results = list(t.get_mean_attack().items())

                sorted_attacker_results = sorted(attacker_results, key=lambda tup: tup[1], reverse=True)

                ################################################################################
                #                                                                              #
                #                              PRINTING                                        #
                #                                                                              #
                ################################################################################

                print("----- Attacker update: ", a, " of round", i)
                print("Fixed Defender Strategy: ", self.fixed_defender[0].get_strategies()[0])

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

                if a == self.single_population_update - 1:

                    new_strategies = []

                    for s in range(0, len(self.attackers[0].get_strategies())):
                        strategy_average = np.mean([x[0].get_strategy_rate(s) for x in sorted_attacker_results[
                                                    0:self.att_keep_number]])

                        self.att_strategy_population_average[s].append(strategy_average)
                        self.att_strategy_population_average_average[s].append(
                            np.mean(self.att_strategy_population_average[s]))

                        new_strategies.append(Periodic(self.att_strategy_population_average_average[s][-1]))

                    self.att_benefit_average.append(
                        np.mean([x[1] for x in sorted_attacker_results[0:self.att_keep_number]]))

                    self.att_benefit_average_average.append(np.mean(self.att_benefit_average))

                    self.fixed_attacker = (Player("Fixed Attacker ",
                                           player_properties=copy(attacker_properties),
                                           strategies=tuple(new_strategies)),)

                else:
                    self.create_new_generation(sorted_attacker_results, self.att_keep_number, i)

            # self.write_in_file(str(i))


tournament_properties = {
    'number_of_rounds': 5,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 1.0
}

game_properties = {
    'time_limit': 1000.0
}

# TODO still don't actually use this mutation rate

ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'data/temp/'
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (1.0, ),
    'threshold': 1
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (8.0, ),
    'threshold': 1
}

attacker_properties = {'move_costs': attacker_ga_properties['move_costs'],
                       'threshold': 1
                       }
defender_properties = {'move_costs': defender_ga_properties['move_costs'],
                       'threshold': 1
                       }

single_attacker = (Player("Attacker ", player_properties=copy(attacker_properties), strategies=(Periodic(0.055), )),)
single_defender = (Player("Defender ", player_properties=copy(defender_properties), strategies=(Periodic(0.166), )),)

ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      system=System(1),
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties)
ga.start(5)
ga.plot()
#
# for i in range(0, 30):
#
#     ga = GeneticAlgorithm(defender_ga_properties, attacker_ga_properties, System(1), ga_properties,
#                           tournament_properties, game_properties)
#
#     ga.start(500)
#
#     ga.write_to_file(i)
# # # #
# #
# ga = GeneticAlgorithm(ga_properties=ga_properties)
# ga.read_from_file(920)
# ga.plot()

#
# plot_universes(ga_properties['file_location'], 30)
