from system import System
from strategies.player import Player
from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
import os
from pathlib import Path



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


class GA:

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

        self.def_top_value = []
        self.att_top_value = []

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

    def start(self, number_of_rounds):
        raise NotImplementedError("No start function implemented")

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

        fig = plt.figure(figsize=(15, 9))

        axs1 = fig.add_subplot(221)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average_average)):
            axs1.plot(self.def_strategy_population_average_average[s])

        axs2 = fig.add_subplot(222)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Payoff')
        plt.title('Defender\'s Payoff Over Time')
        axs2.plot(self.def_benefit_average)

        axs3 = fig.add_subplot(223)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Rate Over Time')
        for s in range(0, len(self.att_strategy_population_average_average)):
            axs3.plot(self.att_strategy_population_average_average[s])

        axs4 = fig.add_subplot(224)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Payoff')
        plt.title('Attacker\'s Payoff Over Time')
        axs4.plot(self.att_benefit_average, 'r')

        plt.show()

    def write_in_file(self, file_number=""):

        self.create_directory(self.ga_properties.get('file_location'))

        # I want a file for defender and attacker
        # Each file has a column for each resource
        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(file_number))
        with open(file, 'w+') as f:
            f.write(str(self.def_strategy_population_average_average))

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(file_number))

        with open(file, 'w+') as f:
            f.write(str(self.att_strategy_population_average_average))

    def create_directory(self, directory):

        if not os.path.exists(directory):
            os.makedirs(directory)



    def write_info_file(self):
        self.create_directory(self.ga_properties.get('file_location'))

        file = Path(self.ga_properties.get('file_location') + 'info_file')
        with open(file, 'w+') as f:
            f.write(str(self.defenders[0].get_player_properties))
            f.write(str(self.attackers[0].get_player_properties))

    def write_to_file(self, file_number=""):

        self.create_directory(self.ga_properties.get('file_location'))

        # I want a file for defender and attacker
        # Each file has a column for each resource
        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(file_number))
        if file.exists():
            if input(" Defender file already exists, are you sure you want to overwrite it? (y/n)") == 'y':
                with open(file, 'w+') as f:
                    f.write(str(self.def_strategy_population_average))

        else:
            with open(file, 'w+') as f:
                f.write(str(self.def_strategy_population_average))

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(file_number))
        if file.exists():
            if input("Attacker file already exists, are you sure you want to overwrite it? (y/n)") == 'y':
                with open(file, 'w+') as f:
                    f.write(str(self.att_strategy_population_average))

        else:
            with open(file, 'w+') as f:
                f.write(str(self.att_strategy_population_average))

    def read_from_file(self, number):

        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(number))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.def_strategy_population_average_average = eval(s)

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(number))
        if file.exists():
            with open(file, 'r') as f:
                s = f.read()
                self.att_strategy_population_average_average = eval(s)

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
