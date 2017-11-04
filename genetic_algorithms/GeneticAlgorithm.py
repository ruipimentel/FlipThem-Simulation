from system import System
from tournament import Tournament
from tournament import TOURNAMENT_TYPE
from strategies.player import Player
from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
import os
from pathlib import Path
import reward_functions


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


class GeneticAlgorithm:

    def __init__(self,
                 defenders=None,
                 attackers=None,
                 system=System(1),
                 ga_properties=example_ga_properties,
                 tournament_properties=example_tournament_properties,
                 game_properties=example_game_properties):

        self.system = system

        # Initiate players
        if defenders is None:
            print("Blank genetic_algorithms created (for now)")
        else:
            if type(defenders) is dict:
                self.defender_ga_properties = defenders
                self.defenders = self.generate_players(defenders, 2.0)
            else:
                self.defender_ga_properties = {'move_costs': defenders[0].get_player_properties()['move_costs']}
                self.defenders = defenders

            if type(attackers) is dict:
                self.attacker_ga_properties = attackers
                self.attackers = self.generate_players(attackers, 2.0)
            else:
                self.attacker_ga_properties = {'move_costs': attackers[0].get_player_properties()['move_costs']}
                self.attackers = attackers

        self.ga_properties = ga_properties
        self.tournament_properties = tournament_properties
        self.game_properties = game_properties

        self.def_strategy_population_average = {}
        self.att_strategy_population_average = {}

        self.def_strategy_population_average_average = {}
        self.att_strategy_population_average_average = {}

        self.def_benefit_average_average = []
        self.att_benefit_average_average = []

        self.att_best_rate = []
        self.def_best_rate = []

        self.def_benefit_average = []
        self.att_benefit_average = []

        self.def_keep_number = 8
        self.att_keep_number = 8


    def generate_players(self, player_ga_properties, upper_bound):
        player_list = []
        for i in range(0, player_ga_properties.get('number_of_players')):
            strategy_list = []
            number_of_strategies = len(player_ga_properties.get('strategy_classes'))

            for server in range(0, len(player_ga_properties.get('move_costs'))):
                strategy_list.append(player_ga_properties.get('strategy_classes')
                                     [np.random.randint(0, number_of_strategies)](np.random.uniform(0, upper_bound)))

            player_properties = {'move_costs': player_ga_properties['move_costs']}

            player_list.append(Player(player_ga_properties.get('name') + str(i),
                                      player_properties=copy(player_properties),
                                      strategies=tuple(strategy_list)))

        return tuple(player_list)

    def start(self, number_of_rounds, file_write=0):

        if file_write == 0:
            file_write = number_of_rounds

        self.write_info_files()

        for s in range(0, len(self.defenders[0].get_strategies())):
            self.def_strategy_population_average[s] = []
            self.att_strategy_population_average[s] = []

            self.def_strategy_population_average_average[s] = []
            self.att_strategy_population_average_average[s] = []

        for i in range(0, number_of_rounds):
            print("------ Round " + str(i + 1) + " --------")

            t = Tournament(defender_strategies=self.defenders,
                           attacker_strategies=self.attackers,
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

            # for r in sorted_defender_results:
            #     rates = []
            #     for strategy in r[0].get_strategies():
            #         rates.append(str(strategy))
            #     print(r[0].get_name(), rates, r[1])
            #
            # print("-------------------")
            #
            # for r in sorted_attacker_results:
            #     rates = []
            #     for strategy in r[0].get_strategies():
            #         rates.append(str(strategy))
            #     print(r[0].get_name(), rates, r[1])

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


    def create_new_generation(self, sorted_results, keep_number, round):

        mas = self.define_parents(keep_number, sorted_results)
        pas = self.define_parents(keep_number, sorted_results)

        for counter1, ma in enumerate(mas):
            # We are creating the offspring to update the sorted results, ready for the next round

            # These will have the same number of strategies (on resources), we iterate through and choose which strategy to take
            offspring_strategies = []
            # Make this a tuple at the end
            for counter2, strategy in enumerate(ma.get_strategies()):
                # 0 is ma, 1 is pa
                if np.random.randint(0, 2) == 0:
                    offspring_strategies.append(strategy)
                else:
                    offspring_strategies.append(pas[counter1].get_strategy(counter2))
            # Create new player, with the strategy
            sorted_results[keep_number + counter1][0].set_strategies(offspring_strategies)

        for result in sorted_results[self.att_keep_number:]:
            for s in range(0, len(result[0].get_strategies())):
                change = 0.1/np.log(round + 2)
                rate = result[0].get_strategy_rate(s)

                result[0].update_strategy_rate(s, rate * (1 + np.random.uniform(-change, change)))
                # print(result[0].get_name(), rate, "---->", result[0].get_strategy_rate(s))

        # Mutation 1
        # mut = np.random.randint(self.att_keep_number, len(sorted_results))
        # strat = np.random.randint(0, self.system.get_number_of_servers())
        # sorted_results[mut][0].update_strategy_rate(strat, np.random.uniform(0, 3))
        # # # Mutation 2
        # mut = np.random.randint(self.att_keep_number, len(sorted_results))
        # strat = np.random.randint(0, self.system.get_number_of_servers())
        # sorted_results[mut][0].update_strategy_rate(strat, np.random.uniform(0, 3))


    def define_parents(self, keep_number, results):
        parents = []

        s = 0
        for r in results:
            s += math.exp(r[1])

        # split = 0.5 * keep_number * (keep_number + 1)
        for ma in range(0, len(results) - keep_number):
            p = np.random.uniform(0, 1)
            start_probability = 0
            end_probability = 0
            for r in results:
                end_probability += math.exp(r[1])
                if start_probability/s <= p < end_probability/s:

                    parents.append(r[0])
                    break
                start_probability = end_probability

        return parents

    def plot(self):

        def_equilibrium, att_equilibrium = reward_functions.exponential.equilibrium(
                                                                    self.tournament_properties['attacker_threshold'],
                                                                    self.defender_ga_properties['move_costs'],
                                                                    self.attacker_ga_properties['move_costs'])

        print("Calculated defender equilibrium", def_equilibrium)
        print("Calculated attacker equilibrium", att_equilibrium)

        def_reward, att_reward = reward_functions.exponential.reward(self.tournament_properties['attacker_threshold'],
                                                                     def_equilibrium,
                                                                     att_equilibrium,
                                                                     self.defender_ga_properties['move_costs'],
                                                                     self.attacker_ga_properties['move_costs'])

        # print("Rewards: ", def_reward, att_reward)
        fig = plt.figure(figsize=(15, 9))

        axs1 = fig.add_subplot(321)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Average Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average_average)):
            axs1.plot(self.def_strategy_population_average_average[s], c=colors[s])
            axs1.plot([def_equilibrium[s]] * len(self.def_strategy_population_average_average[s]), c=colors[s])

        axs2 = fig.add_subplot(323)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average)):
            axs2.plot(self.def_strategy_population_average[s], c=colors[s])
            axs2.plot([def_equilibrium[s]] * len(self.def_strategy_population_average[s]), c=colors[s])

        axs3 = fig.add_subplot(325)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Payoff')
        plt.title('Defender\'s Payoff Over Time')
        axs3.plot(self.def_benefit_average, 'b')
        axs3.plot([def_reward] * len(self.def_benefit_average), 'b')

        axs4 = fig.add_subplot(322)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Average Rate Over Time')
        for s in range(0, len(self.att_strategy_population_average_average)):
            axs4.plot(self.att_strategy_population_average_average[s], c=colors[s])
            axs4.plot([att_equilibrium[s]] * len(self.att_strategy_population_average_average[s]), c=colors[s])

        axs5 = fig.add_subplot(324)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Rate Over Time')
        for s in range(0, len(self.att_strategy_population_average)):
            axs5.plot(self.att_strategy_population_average[s], c=colors[s])
            axs5.plot([att_equilibrium[s]] * len(self.att_strategy_population_average[s]), c=colors[s])

        axs6 = fig.add_subplot(326)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Payoff')
        plt.title('Attacker\'s Payoff Over Time')
        axs6.plot(self.att_benefit_average, 'r')
        axs6.plot([att_reward] * len(self.att_benefit_average), 'r')

        fig.tight_layout()
        plt.show()

    def write_in_file(self, file_number="-1"):

        self.create_directory(self.ga_properties.get('file_location'))
        # I want a file for defender and attacker
        # Each file has a column for each resource
        file = Path(str.strip(self.ga_properties.get('file_location') + 'defender_average_rates_' + str(file_number)))
        with open(file, 'w+') as f:
            f.write(str(self.def_strategy_population_average_average))

        file = Path(self.ga_properties.get('file_location') + 'attacker_average_rates_' + str(file_number))
        with open(file, 'w+') as f:
            f.write(str(self.att_strategy_population_average_average))

        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(file_number))
        with open(file, 'w+') as f:
            f.write(str(self.def_strategy_population_average))

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(file_number))
        with open(file, 'w+') as f:
            f.write(str(self.att_strategy_population_average))

        file = Path(self.ga_properties.get('file_location') + 'defender_payoffs_' + str(file_number))
        with open(file, 'w+') as f:
            f.write(str(self.def_benefit_average))

        file = Path(self.ga_properties.get('file_location') + 'attacker_payoffs_' + str(file_number))
        with open(file, 'w+') as f:
            f.write(str(self.att_benefit_average))


    def create_directory(self, directory):

        if not os.path.exists(directory):
            os.makedirs(directory)



    def write_info_files(self):
        self.create_directory(self.ga_properties.get('file_location') + 'info_files/')

        # Tournament properties
        # Defender GA properties
        # attacker GA properties

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'tournament_properties')
        with open(file, 'w+') as f:
            new_d = copy(self.tournament_properties)
            new_d['tournament_type'] = str(new_d['tournament_type'])
            f.write(str(new_d))

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'defender_ga_properties')
        with open(file, 'w+') as f:
            new_d = copy(self.defender_ga_properties)
            new_d['strategy_classes'] = str(new_d['strategy_classes'])
            f.write(str(new_d))

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'attacker_ga_properties')
        with open(file, 'w+') as f:
            new_d = copy(self.attacker_ga_properties)
            new_d['strategy_classes'] = str(new_d['strategy_classes'])
            f.write(str(new_d))

    def read_from_file(self, file_number):

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'tournament_properties')
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.tournament_properties = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'defender_ga_properties')
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.defender_ga_properties = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'attacker_ga_properties')
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.attacker_ga_properties = eval(s)

        file = Path(str.strip(self.ga_properties.get('file_location') + 'defender_average_rates_' + str(file_number)))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.def_strategy_population_average_average = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'attacker_average_rates_' + str(file_number))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.att_strategy_population_average_average = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(file_number))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.def_strategy_population_average = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(file_number))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.att_strategy_population_average = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'defender_payoffs_' + str(file_number))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.def_benefit_average = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'attacker_payoffs_' + str(file_number))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.att_benefit_average = eval(s)


def plot_universes(location, number):

        def_universes = {}
        for i in range(0, number):
            file = Path(location + 'defender_rates_' + str(i))
            if file.exists():
                with open(file, 'r') as f:
                    s = f.read()
                    def_universes[i] = eval(s)

        att_universes = {}
        for i in range(0, number):
            file = Path(location + 'attacker_rates_' + str(i))
            if file.exists():
                with open(file, 'r') as f:
                    s = f.read()
                    att_universes[i] = eval(s)

        fig = plt.figure(figsize=(15, 9))

        axs1 = fig.add_subplot(211)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Rate Over Time')
        for k, v in def_universes.items():
            axs1.plot(v[0])

        axs2 = fig.add_subplot(212)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Rate Over Time')
        for k, v in att_universes.items():
            axs2.plot(v[0])

        plt.show()
