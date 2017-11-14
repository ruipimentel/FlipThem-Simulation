from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
import os
from pathlib import Path
import reward_functions
import time
import pickle

from tournament import Tournament
from strategies.player import Player

colors = ['#12efff','#eee00f','#e00fff','#123456','#abc222','#000000','#123fff','#1eff1f','#2edf4f','#2eaf9f','#22222f',
          '#eeeff1','#eee112','#00ef00','#aa0000','#0000aa','#000999','#32efff','#23ef68','#2e3f56','#7eef1f','#eeef11']


class GeneticAlgorithm:

    def __init__(self,
                 defenders=None,
                 attackers=None,
                 ga_properties=None,
                 tournament_properties=None,
                 game_properties=None):

        # Initiate players
        if defenders is None:
            print("Blank genetic_algorithms created (for now)")
        else:
            if type(defenders) is dict:
                self.defender_ga_properties = defenders
                self.defenders = self.generate_players(defenders, 2.0)
            else:

                strategies = set()
                for s in defenders[0].get_strategies():
                    print(type(s))
                    strategies.add(type(s))

                self.defender_ga_properties = {'move_costs': defenders[0].get_player_properties()['move_costs'],
                                               'strategy_classes': tuple(strategies),
                                               'number_of_players': len(attackers)}
                self.defenders = defenders

            if type(attackers) is dict:
                self.attacker_ga_properties = attackers
                self.attackers = self.generate_players(attackers, 2.0)
            else:

                strategies = set()
                for s in attackers[0].get_strategies():
                    print(type(s))
                    strategies.add(type(s))
                self.attacker_ga_properties = {'move_costs': attackers[0].get_player_properties()['move_costs'],
                                               'strategy_classes': tuple(strategies),
                                               'number_of_players': len(attackers)}
                self.attackers = attackers

            if len(self.attacker_ga_properties['move_costs']) == len(self.defender_ga_properties['move_costs']):
                self.number_of_servers = len(self.attacker_ga_properties['move_costs'])
            else:
                raise ValueError("Move costs for defender and attacker not equal")

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

        self.def_strategy_count = {}
        self.att_strategy_count = {}

        self.mutation_probability = 0



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

    def __initiate(self):

        self.write_info_files()

        for s in range(0, len(self.defenders[0].get_strategies())):
            self.def_strategy_population_average[s] = []
            self.att_strategy_population_average[s] = []

            self.def_strategy_population_average_average[s] = []
            self.att_strategy_population_average_average[s] = []

            self.def_strategy_count[s] = {}
            self.att_strategy_count[s] = {}


            if self.defender_ga_properties.get('strategy_classes') is None:
                continue
            else:
                for strategy in self.defender_ga_properties['strategy_classes']:
                    self.def_strategy_count[s][strategy] = []


            if self.attacker_ga_properties.get('strategy_classes') is None:
                continue
            else:
                for strategy in self.attacker_ga_properties['strategy_classes']:
                    self.att_strategy_count[s][strategy] = []

    def run(self, number_of_rounds, file_write=0):

        if len(self.def_benefit_average) == 0:
            self.__initiate()
            round_start = 0
            if file_write == 0:
                file_write = number_of_rounds

        else:
            round_start = len(self.def_benefit_average)
            if file_write == 0:
                file_write = number_of_rounds + round_start


        t1 = t2 = time.time()
        for i in range(round_start, number_of_rounds + round_start):

            if i > round_start:
                round_time = t2 - t1
                rounds_left = number_of_rounds + round_start - i
                time_left = round_time * rounds_left
                print("Time left:", str(int(time_left // (60 * 60))) + ":"
                      + str(int((time_left / 60) % 60)) + ":" + str(int(time_left % 60)))

            t1 = time.time()

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
                                                                        sorted_defender_results[
                                                                        0:self.def_keep_number]]))

                self.def_strategy_population_average_average[s].append(
                    np.mean(self.def_strategy_population_average[s]))

                self.att_strategy_population_average[s].append(np.mean([x[0].get_strategy_rate(s)
                                                                        for x in
                                                                        sorted_attacker_results[
                                                                        0:self.att_keep_number]]))

                self.att_strategy_population_average_average[s].append(
                    np.mean(self.att_strategy_population_average[s]))


                def_strategy_list = [x[0].get_strategy(s) for x in sorted_defender_results]
                att_strategy_list = [x[0].get_strategy(s) for x in sorted_attacker_results]

                for strategy in self.defender_ga_properties['strategy_classes']:
                    count = len([s for s in def_strategy_list if type(s) is strategy])
                    self.def_strategy_count[s][strategy].append(count)

                for strategy in self.attacker_ga_properties['strategy_classes']:
                    count = len([s for s in att_strategy_list if type(s) is strategy])
                    self.att_strategy_count[s][strategy].append(count)

            self.def_benefit_average.append(np.mean([x[1] for x in sorted_defender_results[0:self.def_keep_number]]))
            self.att_benefit_average.append(np.mean([x[1] for x in sorted_attacker_results[0:self.att_keep_number]]))

            self.def_benefit_average_average.append(np.mean(self.def_benefit_average))
            self.att_benefit_average_average.append(np.mean(self.att_benefit_average))

            ################################################################################
            #                                                                              #
            #                              PRINTING                                        #
            #                                                                              #
            ################################################################################

            if self.ga_properties.get('print_out'):
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

            if i % file_write == 0 or i == number_of_rounds + round_start - 1:
                self.write_to_file(i)

            t2 = time.time()


    def create_new_generation(self, sorted_results, keep_number, round):

        mas = self.define_parents(keep_number, sorted_results)
        pas = self.define_parents(keep_number, sorted_results)

        for counter1, ma in enumerate(mas):
            # We are creating the offspring to update the sorted results, ready for the next round

            # These will have the same number of strategies (on resources)
            # We iterate through and choose which strategy to take
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

        probability = self.ga_properties['mutation_rate'] * self.number_of_servers * len(sorted_results)

        if probability > 1.0:
            raise ValueError("Mutation Rate too high")
        print("Mutation Probability: ", probability)
        if np.random.choice(2, 1, p=[1-probability, probability]) == 1:
            mut = np.random.randint(self.att_keep_number, len(sorted_results))
            strat = np.random.randint(0, self.number_of_servers)
            sorted_results[mut][0].update_strategy_rate(strat, np.random.uniform(0, 3))



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

    def plot(self, start_time=0, end_time=0, share_axes=False):

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

        print("Rewards: ", def_reward, att_reward)

        if end_time == 0:
            end_time = len(self.def_benefit_average)
        fig = plt.figure(figsize=(15, 9))

        if len(self.defender_ga_properties['strategy_classes']) > 1 \
            or len(self.attacker_ga_properties['strategy_classes']) > 1:

            plot_number = 420
        else:
            plot_number = 320

        axs1 = plt.subplot(plot_number + 1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Average Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average_average)):
            plt.plot(self.def_strategy_population_average_average[s], c=colors[s])
            plt.plot([def_equilibrium[s]] * len(self.def_strategy_population_average_average[s]), c=colors[s])

        axs2 = plt.subplot(plot_number + 3, sharex=axs1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average)):
            plt.plot(self.def_strategy_population_average[s], c=colors[s])
            plt.plot([def_equilibrium[s]] * len(self.def_strategy_population_average[s]), c=colors[s])


        if len(self.defender_ga_properties['strategy_classes']) > 1:
            axs3 = plt.subplot(plot_number + 5, sharex=axs1)
            plt.xlabel('Time (iterations)')
            plt.ylabel('Strategy Count')
            plt.title('Strategy Count Over Time')
            for s in range(0, len(self.def_strategy_count)):
                for counter, p in enumerate(self.def_strategy_count[s]):
                    plt.plot(self.def_strategy_count[s][p], c=colors[counter], label=p.__name__)

            plt.plot([0] * len(self.def_benefit_average), 'r--')
            plt.plot([self.defender_ga_properties['number_of_players']] * len(self.def_benefit_average), 'r--')
            plt.legend()

        else:
            plot_number = plot_number - 2

        axs4 = plt.subplot(plot_number + 7, sharex=axs1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Payoff')
        plt.title('Defender\'s Payoff Over Time')
        plt.plot(self.def_benefit_average, 'b')
        plt.plot([def_reward] * len(self.def_benefit_average), 'b')

        if len(self.defender_ga_properties['strategy_classes']) > 1 \
            or len(self.attacker_ga_properties['strategy_classes']) > 1:

            plot_number = 420
        else:
            plot_number = 320

        axs5 = plt.subplot(plot_number + 2, sharex=axs1, sharey=axs1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Average Rate Over Time')
        for s in range(0, len(self.att_strategy_population_average_average)):
            plt.plot(self.att_strategy_population_average_average[s], c=colors[s])
            plt.plot([att_equilibrium[s]] * len(self.att_strategy_population_average_average[s]), c=colors[s])

        axs6 = plt.subplot(plot_number + 4, sharex=axs1, sharey=axs2)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Rate Over Time')
        for s in range(0, len(self.att_strategy_population_average)):
            plt.plot(self.att_strategy_population_average[s], c=colors[s])
            plt.plot([att_equilibrium[s]] * len(self.att_strategy_population_average[s]), c=colors[s])

        if len(self.attacker_ga_properties['strategy_classes']) > 1:
            axs7 = plt.subplot(plot_number + 6, sharex=axs1, sharey=axs3)
            plt.xlabel('Time (iterations)')
            plt.ylabel('Strategy Count')
            plt.title('Strategy Count Over Time')
            for s in range(0, len(self.att_strategy_count)):
                for counter, p in enumerate(self.att_strategy_count[s]):
                    plt.plot(self.att_strategy_count[s][p], c=colors[counter], label=p.__name__)
            plt.plot([0] * len(self.att_benefit_average), 'r--')
            plt.plot([self.attacker_ga_properties['number_of_players']] * len(self.att_benefit_average), 'r--')
            plt.legend()
        else:
            plot_number = plot_number - 2

        axs8 = plt.subplot(plot_number + 8, sharex=axs1, sharey=axs4)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Payoff')
        plt.title('Attacker\'s Payoff Over Time')
        plt.plot(self.att_benefit_average, 'r')
        plt.plot([att_reward] * len(self.att_benefit_average), 'r')

        plt.xlim(start_time, end_time)

        fig.tight_layout()
        plt.show()

    def write_to_file(self, file_number="-1"):

        self.create_directory(self.ga_properties.get('file_location'))

        file = Path(self.ga_properties.get('file_location') + 'defender_average_rates_' + str(file_number) + ".pkl")
        save_object(obj=self.def_strategy_population_average_average, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'attacker_average_rates_' + str(file_number) + ".pkl")
        save_object(obj=self.att_strategy_population_average_average, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(file_number) + ".pkl")
        save_object(obj=self.def_strategy_population_average, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(file_number) + ".pkl")
        save_object(obj=self.att_strategy_population_average, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'defender_payoffs_' + str(file_number) + ".pkl")
        save_object(obj=self.def_benefit_average, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'attacker_payoffs_' + str(file_number) + ".pkl")
        save_object(obj=self.att_benefit_average, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'last_defender_strategies_' + str(file_number) + ".pkl")
        save_object(obj=self.defenders, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'last_attacker_strategies_' + str(file_number) + ".pkl")
        save_object(obj=self.attackers, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'defender_strategy_count_' + str(file_number) + ".pkl")
        save_object(obj=self.def_strategy_count, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'attacker_strategy_count_' + str(file_number) + ".pkl")
        save_object(obj=self.att_strategy_count, filename=file)


    def create_directory(self, directory):

        if not os.path.exists(directory):
            os.makedirs(directory)



    def write_info_files(self):
        self.create_directory(self.ga_properties.get('file_location') + 'info_files/')

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'ga_properties' + ".pkl")
        save_object(obj=self.ga_properties, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'tournament_properties' + ".pkl")
        save_object(obj=self.tournament_properties, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'defender_ga_properties' + ".pkl")
        save_object(obj=self.defender_ga_properties, filename=file)

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'attacker_ga_properties' + ".pkl")
        save_object(obj=self.attacker_ga_properties, filename=file)

    def read_from_file(self, file_number=None):

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'ga_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.ga_properties = pickle.load(put)

        self.ga_properties['file_location'] = "genetic_algorithms/" + self.ga_properties['file_location']

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'tournament_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.tournament_properties = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'defender_ga_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.defender_ga_properties = pickle.load(put)

        self.number_of_servers = len(self.defender_ga_properties['move_costs'])

        file = Path(self.ga_properties.get('file_location') + 'info_files/' + 'attacker_ga_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.attacker_ga_properties = pickle.load(put)

        directory = os.fsencode(self.ga_properties.get('file_location'))

        if file_number is None:
            max_value = -1
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.startswith("attacker_average_rates"):
                    v = int(filename.split("_")[-1].split(".")[0])
                    max_value = max(max_value, v)

            file_number = str(max_value)

        file = Path(self.ga_properties.get('file_location') + 'defender_average_rates_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.def_strategy_population_average_average = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'attacker_average_rates_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.att_strategy_population_average_average = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.def_strategy_population_average = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.att_strategy_population_average = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'defender_payoffs_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.def_benefit_average = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'attacker_payoffs_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.att_benefit_average = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'last_defender_strategies_' + str(file_number) + ".pkl")
        with open(file, 'rb') as put:
            self.defenders = pickle.load(put)

        file = Path(self.ga_properties.get('file_location') + 'last_attacker_strategies_' + str(file_number) + ".pkl")
        with open(file, 'rb') as put:
            self.attackers = pickle.load(put)

        file = Path(
            self.ga_properties.get('file_location') + 'defender_strategy_count_' + str(file_number) + ".pkl")
        with open(file, 'rb') as put:
            self.def_strategy_count = pickle.load(put)

            file = Path(
                self.ga_properties.get('file_location') + 'attacker_strategy_count_' + str(file_number) + ".pkl")
            with open(file, 'rb') as put:
                self.att_strategy_count = pickle.load(put)


def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

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
