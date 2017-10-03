from mp_tournament import Tournament
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


# Can i speed this up by the changing population only playing the top performing strategies from the other population
# Perhaps put some kind of weighting in there??


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
            print("Blank GA created (for now)")
        else:
            if type(defenders) is dict:
                self.defenders = self.generate_players(defenders, 3.0)
            else:
                self.defenders = defenders

            if type(attackers) is dict:
                self.attackers = self.generate_players(attackers, 3.0)
            else:
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

        self.single_population_update = 10

        self.fixed_defender = (Player("Fixed Defender ",
                                      player_properties=copy(defender_properties),
                                      strategies=(Periodic(np.random.uniform(0.0, 0.5)),)),)
        self.fixed_attacker = (Player("Fixed Attacker ",
                                      player_properties=copy(attacker_properties),
                                      strategies=(Periodic(np.random.uniform(0.0, 0.5)),)),)


    def generate_players(self, player_ga_properties, upper_bound):
        player_list = []
        for i in range(0, player_ga_properties.get('number_of_players')):
            strategy_list = []
            number_of_strategies = len(player_ga_properties.get('strategy_classes'))

            for server in range(0, self.system.get_number_of_servers()):
                strategy_list.append(player_ga_properties.get('strategy_classes')
                                     [np.random.randint(0, number_of_strategies)](np.random.uniform(0, upper_bound)))

            player_properties = {'move_costs': player_ga_properties['move_costs'],
                                 'threshold': player_ga_properties['threshold']}

            player_list.append(Player(player_ga_properties.get('name') + str(i),
                                      player_properties=copy(player_properties),
                                      strategies=tuple(strategy_list)))

        return tuple(player_list)

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

            self.write_in_file(str(i))

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
        mut = np.random.randint(self.att_keep_number, len(sorted_results))
        strat = np.random.randint(0, self.system.get_number_of_servers())
        sorted_results[mut][0].update_strategy_rate(strat, np.random.uniform(0, 3))
        # # Mutation 2
        mut = np.random.randint(self.att_keep_number, len(sorted_results))
        strat = np.random.randint(0, self.system.get_number_of_servers())
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


    def plot(self):

        fig = plt.figure(figsize=(15, 9))

        axs1 = fig.add_subplot(221)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Average Rate Over Time')
        for s in range(0, len(self.def_strategy_population_average_average)):
            axs1.plot(self.def_strategy_population_average_average[s], 'b')

        axs2 = fig.add_subplot(222)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Payoff')
        plt.title('Defender\'s Payoff Over Time')
        # plt.title('Defender\'s Rate Over Time')
        axs2.plot(self.def_benefit_average)
        # for s in range(0, len(self.def_strategy_population_average)):
        #     axs2.plot(self.def_strategy_population_average[s], 'b')

        axs3 = fig.add_subplot(223)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Rate Over Time')
        for s in range(0, len(self.att_strategy_population_average_average)):
            axs3.plot(self.att_strategy_population_average_average[s], 'r')

        axs4 = fig.add_subplot(224)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Payoff Over Time')
        axs4.plot(self.att_benefit_average, 'r')
        # plt.title('Attacker\'s Rate Over Time')
        axs2.plot(self.def_benefit_average)
        # for s in range(0, len(self.att_strategy_population_average)):
        #     axs4.plot(self.att_strategy_population_average[s], 'r')

        plt.show()

    def write_in_file(self, file_number=""):

        # if not os.path.exists(self.def_):
        #     os.makedirs(directory)

        # I want a file for defender and attacker
        # Each file has a column for each resource
        file = Path(self.ga_properties.get('file_location') + 'defender_rates_' + str(file_number))
        with open(file, 'w+') as f:
            f.write(str(self.def_strategy_population_average_average))

        file = Path(self.ga_properties.get('file_location') + 'attacker_rates_' + str(file_number))

        with open(file, 'w+') as f:
            f.write(str(self.att_strategy_population_average_average))

    def write_to_file(self, file_number=""):

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


def def_equilibrium(server, defender_costs, attacker_costs):

    product = attacker_costs[server] / ((attacker_costs[server] + defender_costs[server]) ** 2)
    for i in range(0, len(defender_costs)):
        if i != server:

            product *= (defender_costs[i] / (attacker_costs[i] + defender_costs[i]))

    return product


def calculate_periodic_equilibrium(defender_cost, attacker_cost):

    if defender_cost < attacker_cost:
        return 1 / (2 * attacker_cost), defender_cost / (2 * attacker_cost ** 2)
    elif defender_cost == attacker_cost:
        return 1 / (2 * defender_cost), 1 / (2 * defender_cost)
    else:
        return attacker_cost / (2 * defender_cost ** 2), 1 / (2 * defender_cost)


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
    'file_location': 'data/crap/'
}

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,
    'strategy_classes': (Periodic,),
    'move_costs': (1.0, ),
    'threshold': 1
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'strategy_classes': (Periodic,),
    'move_costs': (3.0, ),
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
                      tournament_properties=tournament_properties,
                      game_properties=game_properties)
ga.start(20)
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
# ga.read_from_file(160)
# ga.plot()

#
# plot_universes(ga_properties['file_location'], 30)
