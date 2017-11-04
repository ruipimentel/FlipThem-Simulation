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
import os
from genetic_algorithms.GeneticAlgorithm import GeneticAlgorithm
import reward_functions.exponential

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


colors = ['#12efff','#eee00f','#e00fff','#123456','#abc222','#000000','#123fff','#1eff1f','#2edf4f','#2eaf9f','#22222f',
        '#eeeff1','#eee112','#00ef00','#aa0000','#0000aa','#000999','#32efff','#23ef68','#2e3f56','#7eef1f','#eeef11']



# What about instead of players updating their populations "simultaneously", the defender finds the best response
# to the current attacker population, then the attacker responds to that defenders population
# So on and so forth.


# Can i speed this up by the changing population only playing the top performing strategies from the other population
# Perhaps put some kind of weighting in there??


class GeneticAlgorithm(GeneticAlgorithm):

    def __init__(self,
                 defenders=None,
                 attackers=None,
                 system=System(1),
                 ga_properties=example_ga_properties,
                 tournament_properties=example_tournament_properties,
                 game_properties=example_game_properties):

        super().__init__(defenders, attackers, system, ga_properties, tournament_properties, game_properties)
        self.single_population_update = 10

        defender_strategies = [Exponential(np.random.uniform(0.0, 0.5)) for c in
                               self.defenders[0].get_player_properties()['move_costs']]

        self.fixed_defender = (Player("Fixed Defender ",
                                      player_properties=copy(defender_properties),
                                      strategies=tuple(defender_strategies)),)

        attacker_strategies = [Exponential(np.random.uniform(0.0, 0.5)) for c in
                               self.attackers[0].get_player_properties()['move_costs']]

        self.fixed_attacker = (Player("Fixed Attacker ",
                                      player_properties=copy(attacker_properties),
                                      strategies=tuple(attacker_strategies)),)


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

                # Play tournament
                if i > 0:
                    self.system = System(self.system.get_number_of_servers())
                    # If we have already done one round, we take the average of the attackers
                    # strategies in order to speed up the process

                t = Tournament(defender_strategies=self.defenders, attacker_strategies=self.fixed_attacker,
                               system=self.system, game_properties=example_game_properties,
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

                # Play tournament
                if i > 0:
                    self.system = System(self.system.get_number_of_servers())

                t = Tournament(defender_strategies=self.fixed_defender, attacker_strategies=self.attackers,
                               system=self.system, game_properties=example_game_properties,
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

    def plot(self):

        def_equilibrium, att_equilibrium = reward_functions.exponential.equilibrium(self.tournament_properties['attacker_threshold'],
                                                                                    self.defender_ga_properties['move_costs'],
                                                                                    self.attacker_ga_properties['move_costs'])


        def_reward, att_reward = reward_functions.exponential.reward(self.tournament_properties['attacker_threshold'],
                                                                     def_equilibrium,
                                                                     att_equilibrium,
                                                                     self.defender_ga_properties['move_costs'],
                                                                     self.attacker_ga_properties['move_costs'])

        print('Rewards: ', def_reward, att_reward)

        # test_def_equilibrium, test_att_equilibrium = reward_functions.exponential.full_threshold_equilibrium(2, self.defender_ga_properties['move_costs'],
        #                                                         self.attacker_ga_properties['move_costs'])

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
    'selection_ratio': 1.0
}

game_properties = {
    'time_limit': 10000.0
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
    'move_costs': (0.5040,),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.25,),
}


attacker_properties = {'move_costs': attacker_ga_properties['move_costs'],
                       'threshold': tournament_properties['attacker_threshold']
                       }
defender_properties = {'move_costs': defender_ga_properties['move_costs'],
                       'threshold': tournament_properties['defender_threshold']
                       }
ga = GeneticAlgorithm(defenders=defender_ga_properties,
                      attackers=attacker_ga_properties,
                      system=System(1),
                      ga_properties=ga_properties,
                      tournament_properties=tournament_properties,
                      game_properties=game_properties)


ga.start(50)
ga.plot()
#

# genetic_algorithms.start(2000)
# genetic_algorithms.plot()
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
# ga = GeneticAlgorithm(ga_properties=ga_properties)
# ga.read_from_file(920)
# ga.plot()

#
# plot_universes(ga_properties['file_location'], 30)