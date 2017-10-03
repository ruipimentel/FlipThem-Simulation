from deterministic_tournament import DeterministicTournament
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.exponential import Exponential
from strategies.player import Player
import reward_functions.exponential
from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
from GA import GA
import os

# TODO: Decide on mutation
# TODO: Generalise to allow any strategy
# TODO: Clean up the shitty code
# We are keeping the keep rate constant at 50% for now

colors = ['#12efff','#eee00f','#e00fff','#123456','#abc222','#000000','#123fff','#1eff1f','#2edf4f','#2eaf9f','#22222f',
        '#eeeff1','#eee112','#00ef00','#aa0000','#0000aa','#000999','#32efff','#23ef68','#2e3f56','#7eef1f','#eeef11']

example_tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 3,
    'defender_threshold': 1,
}

# TODO still don't actually use this
example_ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'data/'
}


class DeterministicGeneticAlgorithm(GA):

    def start(self, number_of_rounds, file_write=5):

        self.write_info_file()


        for s in range(0, len(self.defenders[0].get_strategies())):
            self.def_strategy_population_average[s] = []
            self.att_strategy_population_average[s] = []

            self.def_strategy_population_average_average[s] = []
            self.att_strategy_population_average_average[s] = []

        for i in range(0, number_of_rounds):
            print("------ Round " + str(i + 1) + " --------")

            t = DeterministicTournament(defender_strategies=self.defenders, attacker_strategies=self.attackers,
                                        tournament_properties=self.tournament_properties)

            t.play_tournament()

            # Organise the results
            defender_results = list(t.get_mean_defense().items())

            attacker_results = list(t.get_mean_attack().items())

            sorted_defender_results = sorted(defender_results, key=lambda tup: tup[1], reverse=True)
            sorted_attacker_results = sorted(attacker_results, key=lambda tup: tup[1], reverse=True)

            for s in range(0, len(self.defenders[0].get_strategies())):
                self.def_strategy_population_average[s].append(np.mean([x[0].get_strategy_rate(s)
                                                                        for x in
                                                                        sorted_defender_results[0:self.def_keep_number]]))

                self.def_strategy_population_average_average[s].append(
                    np.mean(self.def_strategy_population_average[s]))

            for s in range(0, len(self.attackers[0].get_strategies())):
                self.att_strategy_population_average[s].append(np.mean([x[0].get_strategy_rate(s)
                                                                        for x in
                                                                        sorted_attacker_results[0:self.att_keep_number]]))

                self.att_strategy_population_average_average[s].append(
                    np.mean(self.att_strategy_population_average[s]))

            self.def_benefit_average.append(np.mean([x[1] for x in sorted_defender_results[0:self.def_keep_number]]))
            self.att_benefit_average.append(np.mean([x[1] for x in sorted_attacker_results[0:self.att_keep_number]]))

            self.def_benefit_average_average.append(np.mean(self.def_benefit_average))
            self.att_benefit_average_average.append(np.mean(self.att_benefit_average))

            # Organise the results
            defender_results = list(t.get_mean_defense().items())

            sorted_defender_results = sorted(defender_results, key=lambda tup: tup[1], reverse=True)

            ################################################################################
            #                                                                              #
            #                              PRINTING                                        #
            #                                                                              #
            ################################################################################


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

            if len(self.attackers) > 1:
                self.create_new_generation(sorted_attacker_results, self.att_keep_number, i)

            if i % file_write == 0 or i == number_of_rounds - 1:
                self.write_in_file(i)

    def plot(self):

        def_equilibrium, att_equilibrium = reward_functions.exponential.equilibrium(self.tournament_properties['attacker_threshold'],
                                                                                    self.defender_ga_properties['move_costs'],
                                                                                    self.attacker_ga_properties['move_costs'])

        def_reward, att_reward = reward_functions.exponential.reward(self.tournament_properties['attacker_threshold'],
                                            def_equilibrium,
                                            att_equilibrium,
                                            self.defender_ga_properties['move_costs'],
                                            self.attacker_ga_properties['move_costs'])

        fig = plt.figure(figsize=(15, 9))

        axs1 = fig.add_subplot(221)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average_average)):
            axs1.plot(self.def_strategy_population_average_average[s], c=colors[s])
            axs1.plot([def_equilibrium[s]] * len(self.def_strategy_population_average_average[s]), c=colors[s])

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

        axs4 = fig.add_subplot(224)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Payoff')
        plt.title('Attacker\'s Payoff Over Time')
        axs4.plot(self.att_benefit_average, 'r')
        axs4.plot([att_reward] * len(self.att_benefit_average), 'r')

        plt.show()


tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 3,
    'defender_threshold': 1,
    'selection_ratio': 1.0
}

# TODO still don't actually use this mutation rate

ga_properties = {
    'mutation_rate': 0.2,
    'file_location': 'data/Deterministic/GA/Exponential/'
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.2, 0.3, 0.1),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Exponential,),
    'move_costs': (0.1, 0.2, 0.3),
}

ga = DeterministicGeneticAlgorithm(defenders=defender_ga_properties,
                                   attackers=attacker_ga_properties,
                                   ga_properties=ga_properties,
                                   tournament_properties=tournament_properties)
ga.start(100, 20)
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
# # #
# ga = DeterministicGeneticAlgorithm(ga_properties=ga_properties)
# ga.read_from_file(700)
# ga.plot()

#
# plot_universes(ga_properties['file_location'], 30)
