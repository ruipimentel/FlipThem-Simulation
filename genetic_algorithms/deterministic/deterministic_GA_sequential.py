from deterministic_tournament import DeterministicTournament
from strategies.server_strategies.exponential import Exponential
from strategies.player import Player
from system import System
import reward_functions.exponential
from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
import os
from genetic_algorithms.GA import GA


colors = ['#12efff','#eee00f','#e00fff','#123456','#abc222','#000000','#123fff','#1eff1f','#2edf4f','#2eaf9f','#22222f',
        '#eeeff1','#eee112','#00ef00','#aa0000','#0000aa','#000999','#32efff','#23ef68','#2e3f56','#7eef1f','#eeef11']


#
# TODO: Better Ranking system
# TODO: Decide on mutation
# TODO: Generalise to allow any strategy
# TODO: Clean up the shitty code
# We are keeping the keep rate constant at 50% for now

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.2,),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.1,),
}
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


def t_defender_equilibrium(costs):
    return costs[1]/(costs[0] + costs[1])**2

def t_attacker_equilibrium(costs):
    return costs[0]/(costs[0] + costs[1])**2



class GeneticAlgorithm(GA):

    def __init__(self,
                 defenders=None,
                 attackers=None,
                 system=System(1),
                 ga_properties=example_ga_properties,
                 tournament_properties=example_tournament_properties):

        super().__init__(defenders, attackers, system, ga_properties, tournament_properties)

        self.single_population_update = 10

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

                t = DeterministicTournament(defender_strategies=self.defenders, attacker_strategies=self.attackers,
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


                    for s in range(0, len(self.defenders[0].get_strategies())):
                        strategy_average = np.mean([x[0].get_strategy_rate(s)
                                                    for x in sorted_defender_results[0:self.def_keep_number]])

                        self.def_strategy_population_average[s].append(strategy_average)

                        self.def_strategy_population_average_average[s].append(np.mean
                                                                               (self.def_strategy_population_average[s])
                                                                               )

                    self.def_benefit_average.append(np.mean([x[1] for x in sorted_defender_results[0:self.def_keep_number]]))

                    self.def_benefit_average_average.append(np.mean(self.def_benefit_average))

                else:
                    self.create_new_generation(sorted_defender_results, self.def_keep_number, i)

            for a in range(0, self.single_population_update):
                # Here the attacker updates his rates

                t = DeterministicTournament(defender_strategies=self.defenders, attacker_strategies=self.attackers,
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


                    for s in range(0, len(self.attackers[0].get_strategies())):
                        strategy_average = np.mean([x[0].get_strategy_rate(s) for x in sorted_attacker_results[
                                                    0:self.att_keep_number]])

                        self.att_strategy_population_average[s].append(strategy_average)
                        self.att_strategy_population_average_average[s].append(
                            np.mean(self.att_strategy_population_average[s]))

                    self.att_benefit_average.append(
                        np.mean([x[1] for x in sorted_attacker_results[0:self.att_keep_number]]))

                    self.att_benefit_average_average.append(np.mean(self.att_benefit_average))

                else:
                    self.create_new_generation(sorted_attacker_results, self.att_keep_number, i)

            self.write_in_file(str(i))

    def plot(self):

        def_equilibrium, att_equilibrium = reward_functions.exponential.equilibrium(self.tournament_properties['attacker_threshold'],
                                                                                    self.defender_ga_properties['move_costs'],
                                                                                    self.attacker_ga_properties['move_costs'])

        # test_def_equilibrium = t_defender_equilibrium((self.defender_ga_properties['move_costs'][0],
        #                                         self.attacker_ga_properties['move_costs'][0]))
        #
        # test_att_equilibrium = t_attacker_equilibrium((self.defender_ga_properties['move_costs'][0],
        #                                         self.attacker_ga_properties['move_costs'][0]))
        #
        # print(def_equilibrium[0] == test_def_equilibrium, att_equilibrium[0] == test_att_equilibrium)

        print("Calculated defender equilibrium", def_equilibrium)
        print("Calculated attacker equilibrium", att_equilibrium)

        def_reward, att_reward = reward_functions.exponential.reward(self.tournament_properties['attacker_threshold'],
                                                                     def_equilibrium,
                                                                     att_equilibrium,
                                                                     self.defender_ga_properties['move_costs'],
                                                                     self.attacker_ga_properties['move_costs'])

        print("Rewards: ", def_reward, att_reward)
        fig = plt.figure(figsize=(15, 9))

        axs1 = fig.add_subplot(221)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average_average)):
            axs1.plot(self.def_strategy_population_average_average[s], c=colors[s])
            axs1.plot([def_equilibrium[s]] * len(self.def_strategy_population_average_average[s]), c=colors[s])
            # axs1.plot([test_def_equilibrium] * len(self.def_strategy_population_average_average[s]), c='r')

        axs2 = fig.add_subplot(222)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Payoff')
        plt.title('Defender\'s Payoff Over Time')
        axs2.plot(self.def_benefit_average, 'b')
        axs2.plot([def_reward] * len(self.def_benefit_average), 'b')

        axs3 = fig.add_subplot(223)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Rate Over Time')
        for s in range(0, len(self.att_strategy_population_average_average)):
            axs3.plot(self.att_strategy_population_average_average[s], c=colors[s])
            axs3.plot([att_equilibrium[s]] * len(self.att_strategy_population_average_average[s]), c=colors[s])
            # axs3.plot([test_att_equilibrium] * len(self.att_strategy_population_average_average[s]), c='r')

        axs4 = fig.add_subplot(224)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Payoff')
        plt.title('Attacker\'s Payoff Over Time')
        axs4.plot(self.att_benefit_average, 'r')
        axs4.plot([att_reward] * len(self.att_benefit_average), 'r')

        plt.show()


tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.6
}

# TODO still don't actually use this mutation rate

ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'data/current/'
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.2,),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.1,),
}


ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties)
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
# #
# genetic_algorithms = GeneticAlgorithm(ga_properties=ga_properties)
# genetic_algorithms.read_from_file(920)
# genetic_algorithms.plot()

#
# plot_universes(ga_properties['file_location'], 30)
