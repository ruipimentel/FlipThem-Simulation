from __future__ import annotations

from typing import Tuple, List, Dict, TYPE_CHECKING

from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
import os
from pathlib import Path
import reward_functions
import time
import pickle

from core.tournament import Tournament
from strategies.player import Player

if TYPE_CHECKING:
    from numpy import NDArray
    from strategies.server_strategies.server_strategy import ServerStrategy

colors = ['#12efff','#eee00f','#e00fff','#123456','#abc222','#000000','#123fff','#1eff1f','#2edf4f','#2eaf9f','#22222f',
          '#eeeff1','#eee112','#00ef00','#aa0000','#0000aa','#000999','#32efff','#23ef68','#2e3f56','#7eef1f','#eeef11']

other_colors = ['#12efff','#e00fff','#eee00f','#123456','#abc222','#000000','#123fff','#1eff1f','#2edf4f','#2eaf9f','#22222f',
          '#eeeff1','#eee112','#00ef00','#aa0000','#0000aa','#000999','#32efff','#23ef68','#2e3f56','#7eef1f','#eeef11']


class GeneticAlgorithm:

    def __init__(self,
                 defenders: (Dict | Tuple[Player, ...] | None) = None,
                 attackers: (Dict | Tuple[Player, ...] | None) = None,
                 ea_properties: (Dict | None) = None,
                 tournament_properties: (Dict | None) = None,
                 game_properties: (Dict | None) = None):

        self.ea_properties: (Dict | None) = ea_properties
        # Initiate players
        if defenders is None:
            print("Blank genetic_algorithms created (for now)")
        else:
            self.defender_ea_properties, self.defenders = self.initialize_players(defenders, attackers)
            self.attacker_ea_properties, self.attackers = self.initialize_players(attackers, attackers)

            if len(self.attacker_ea_properties['move_costs']) == len(self.defender_ea_properties['move_costs']):
                self.number_of_servers: int = len(self.attacker_ea_properties['move_costs'])
            else:
                raise ValueError("Number of move costs for defender and attacker not equal")

        self.tournament_properties: (Dict | None) = tournament_properties
        self.game_properties: (Dict | None) = game_properties

        self.defender_population: Dict[int, List[float] | NDArray[float]] = {}
        self.attacker_population: Dict[int, List[float] | NDArray[float]] = {}

        self.defender_benefit: (List[float] | NDArray[float]) = []
        self.attacker_benefit: (List[float] | NDArray[float]) = []

        # self.def_benefit_average = []
        # self.att_benefit_average = []

        self.def_keep_number: int = 8
        self.att_keep_number: int = 8

        self.def_strategy_count: Dict[int, Dict[ServerStrategy, List[int]]] = {}
        self.att_strategy_count: Dict[int, Dict[ServerStrategy, List[int]]] = {}

        self.mutation_probability: float = 0

    def initialize_players(
        self,
        players: (Dict | Tuple[Player, ...]),
        attackers: (Dict | Tuple[Player, ...]),
    ) -> Tuple[Dict, Tuple[Player, ...]]:
        """
        When given a properties Dict, returns it along with the actual players
        generated via `generate_players`.
        When given players, generates a properties Dict, then returns it along
        with the received players.
        """

        if type(players) is dict:
            return (
                players,
                self.generate_players(players),
            )
        else:
            strategies = set()
            for s in players[0].get_strategies():
                strategies.add(type(s))
            return (
                {
                    'move_costs': players[0].get_player_properties()['move_costs'],
                    'strategy_classes': tuple(strategies),
                    'number_of_players': len(attackers),
                },
                players,
            )

    def generate_players(self, player_ea_properties: Dict) -> Tuple[Player, ...]:
        """
        Generates the amount of `Player` instances provided by the properties Dict.
        Each player will have 1 strategy class (taken randomly from the pool of
        available strategy classes) for each server. Each strategy has one random
        rate lying in the range given by the GA properties Dict stored in `self`.

        Also, each player will have a player properties Dict whose `move_costs`
        attribute mirrors that of the specified properties Dict.

        `player_ea_properties` should include the following keys:
        - `number_of_players` (`int`): The number of players to generate.
        - `strategy_classes` (`Iterable[Type[Strategy]]`): The strategy classes to
          choose from.
        - `move_costs` (`List[float]`): A list of move costs for the servers.
        """

        player_list = []
        number_of_players = player_ea_properties.get('number_of_players')
        for i in range(0, number_of_players):
            strategy_list = []
            # Number of strategy classes:
            number_of_strategies = len(player_ea_properties.get('strategy_classes'))
            # Number of servers in play:
            number_of_servers = len(player_ea_properties.get('move_costs'))

            for server in range(0, number_of_servers):
                strategy_list.append(player_ea_properties.get('strategy_classes')[
                    np.random.randint(0, number_of_strategies)
                ](np.random.uniform(
                    self.ea_properties['lower_bound'],
                    self.ea_properties['upper_bound'],
                )))

            player_properties = {'move_costs': player_ea_properties['move_costs']}

            player_list.append(Player(player_ea_properties.get('name') + str(i),
                                      player_properties=copy(player_properties),
                                      strategies=tuple(strategy_list)))

        return tuple(player_list)

    def __initiate(self) -> None:

        self.write_info_files()

        for s in range(0, len(self.defenders[0].get_strategies())):

            self.defender_population[s] = []
            self.attacker_population[s] = []

            self.def_strategy_count[s] = {}
            self.att_strategy_count[s] = {}

            if self.defender_ea_properties.get('strategy_classes') is None:
                continue
            else:
                for strategy in self.defender_ea_properties['strategy_classes']:
                    self.def_strategy_count[s][strategy] = []

            if self.attacker_ea_properties.get('strategy_classes') is None:
                continue
            else:
                for strategy in self.attacker_ea_properties['strategy_classes']:
                    self.att_strategy_count[s][strategy] = []

    def run(self, number_of_rounds: int, file_write: int = 0) -> None:

        if len(self.defender_benefit) == 0:
            self.__initiate()
            round_start = 0
        else:
            round_start = len(self.defender_benefit)

        # Default value for `file_write` in case it is not specified:
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

            sorted_defender_results: List[Tuple[Player, float]] = sorted(
                defender_results,
                key=lambda tup: tup[1],
                reverse=True,
            )

            sorted_attacker_results: List[Tuple[Player, float]] = sorted(
                attacker_results,
                key=lambda tup: tup[1],
                reverse=True,
            )

            self.update_plot_data(sorted_defender_results, sorted_attacker_results)

            ################################################################################
            #                                                                              #
            #                              PRINTING                                        #
            #                                                                              #
            ################################################################################

            if self.ea_properties.get('print_out'):
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

            if len(self.defenders) > 1 and self.ea_properties['defender_update']:
                self.create_new_generation(sorted_defender_results, self.def_keep_number, self.defender_ea_properties, i)

            if len(self.attackers) > 1 and self.ea_properties['attacker_update']:
                self.create_new_generation(sorted_attacker_results, self.att_keep_number, self.attacker_ea_properties, i)

            if i % file_write == 0 or i == number_of_rounds + round_start - 1:
                self.write_to_file(i)

            t2 = time.time()


    def create_new_generation(
        self,
        sorted_results: List[Tuple[Player, float]],
        keep_number: int,
        player_ea_properties: Dict,
        round: int,
    ) -> None:
        """
        Mutates `sorted_results` list by replacing `Player`'s strategies with new
        strategies chosen from 2 random parent populations (mothers and fathers),
        and also by modifying their rate with a random perturbation. This random
        perturbation tends to be smaller after each round.

        The mothers and fathers are randomly chosen using `define_parents` method.
        """

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

        probability = self.ea_properties['mutation_rate'] * len(sorted_results)

        if probability > 1.0:
            raise ValueError("Mutation Rate too high")
        # print("Mutation Probability: ", probability)
        for n in range(0, self.number_of_servers):
            if np.random.choice(2, 1, p=[1-probability, probability]) == 1:
                mut = np.random.randint(self.att_keep_number, len(sorted_results))
                serv = np.random.randint(0, self.number_of_servers)
                strategy_class = player_ea_properties['strategy_classes'][
                    np.random.randint(0, len(player_ea_properties['strategy_classes']))
                ]
                sorted_results[mut][0].update_strategy(serv, strategy_class(np.random.uniform(
                    self.ea_properties['lower_bound'], self.ea_properties['upper_bound'])))

                # sorted_results[mut][0].update_strategy_rate(serv, np.random.uniform(0, 3))

    def define_parents(
        self,
        keep_number: int,
        results: List[Tuple[Player, float]],
    ) -> List[Player]:
        """
        Produces a list of length `len(results) - keep_number` of tuples taken from
        `results`. These tuples are chosen randomly with probability given by a
        Logit probability function — that is, the tuples are chosen with probability
        proportional to a weight `w = exp(average_benefit)/s`, where `s` is the sum
        of every `exp(average_benefit)` in `results`.
        """

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

    def update_plot_data(
        self,
        sorted_defender_results: List[Tuple[Player, float]],
        sorted_attacker_results: List[Tuple[Player, float]],
    ) -> None:

        for s in range(0, len(self.defenders[0].get_strategies())):

            # Updates the list of defender rates on this server:
            self.update_sorted_player_rates_for_server(
                sorted_defender_results,
                self.defender_population,
                s,
            )

            # Updates the list of attacker rates on this server:
            self.update_sorted_player_rates_for_server(
                sorted_attacker_results,
                self.attacker_population,
                s,
            )

            # Updates the defender strategy-class count on this server:
            self.update_player_strategy_count_for_server(
                self.def_strategy_count,
                sorted_defender_results,
                self.defender_ea_properties,
                s,
            )

            # Updates the attacker strategy-class count on this server:
            self.update_player_strategy_count_for_server(
                self.att_strategy_count,
                sorted_attacker_results,
                self.attacker_ea_properties,
                s,
            )

        self.defender_benefit = self.concatenate_player_benefit(
            [[x[1] for x in sorted_defender_results]],
            self.defender_benefit,
        )

        self.attacker_benefit = self.concatenate_player_benefit(
            [[x[1] for x in sorted_attacker_results]],
            self.attacker_benefit,
        )

    def update_sorted_player_rates_for_server(
        self,
        sorted_player_results: List[Tuple[Player, float]],
        player_population: Dict[int, List[float] | NDArray[float]],
        server: int,
    ) -> None:
        current_player_generation_rates = [x[0].get_strategy_rate(server) for x in sorted_player_results]
        np_current_player_generation_rates = np.array([current_player_generation_rates])

        if type(player_population[server]) == list:
            # If player population is still a list, then it's empty (we're in generation 1):
            player_population[server] = np_current_player_generation_rates
        else:
            # Otherwise, it's already a partially populated `NDArray`:
            player_population[server] = np.concatenate(
                (player_population[server], np_current_player_generation_rates),
                axis=0,
            )

    def update_player_strategy_count_for_server(
        self,
        player_strategy_count: Dict[int, Dict[ServerStrategy, List[int]]],
        sorted_player_results: List[Tuple[Player, float]],
        player_ea_properties: Dict,
        server: int,
    ) -> None:
        # Strategies used by this class of player on the specified server:
        player_strategy_list = [x[0].get_strategy(server) for x in sorted_player_results]
        for strategy in player_ea_properties['strategy_classes']:
            count = len([s for s in player_strategy_list if type(s) is strategy])
            player_strategy_count[server][strategy].append(count)

    def concatenate_player_benefit(
        self,
        new_benefits: List[List[float]],
        player_benefit: (List[float] | NDArray[float]),
    ) -> NDArray[float]:
        if type(player_benefit) is list:
            return np.array(new_benefits)
        else:
            return np.concatenate((player_benefit, new_benefits), axis=0)

    def plot(self, start_time: float = 0, end_time: float = 0, share_axes: bool = False) -> None:

        # def_equilibrium, att_equilibrium = reward_functions.exponential.equilibrium(
        #                                                             self.tournament_properties['attacker_threshold'],
        #                                                             self.defender_ea_properties['move_costs'],
        #                                                             self.attacker_ea_properties['move_costs'])

        # print("Calculated defender equilibrium", def_equilibrium)
        # print("Calculated attacker equilibrium", att_equilibrium)
        #
        # def_reward, att_reward = reward_functions.exponential.reward(self.tournament_properties['attacker_threshold'],
        #                                                              def_equilibrium,
        #                                                              att_equilibrium,
        #                                                              self.defender_ea_properties['move_costs'],
        #                                                              self.attacker_ea_properties['move_costs'])
        #
        # print("Rewards: ", def_reward, att_reward)

        if end_time == 0:
            end_time = len(self.defender_benefit)
        fig = plt.figure(figsize=(15, 9))

        if len(self.defender_ea_properties['strategy_classes']) > 1 \
            or len(self.attacker_ea_properties['strategy_classes']) > 1:

            plot_number = 420
        else:
            plot_number = 320

        axs1 = plt.subplot(plot_number + 1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Average Rate Over Time')
        # TODO This needs to be average of the average
        for s in range(0, len(self.defender_population)):
            m = np.mean(self.defender_population[s][:, 0:self.def_keep_number], axis=1)
            mean_of_mean = [np.mean(m[:c+1]) for c, t in enumerate(m)]
            plt.plot(mean_of_mean, c=colors[s])
            # plt.plot([def_equilibrium[s]] * len(self.defender_population[s]), c=colors[s])

        axs2 = plt.subplot(plot_number + 3, sharex=axs1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Rate')
        plt.title('Defender\'s Rate Over Time')
        for s in range(0, len(self.defender_population)):
            m = np.mean(self.defender_population[s][:, 0:self.def_keep_number], axis=1)
            plt.plot(m, c=colors[s])
            # plt.plot([def_equilibrium[s]] * len(self.defender_population[s]), c=colors[s])


        if len(self.defender_ea_properties['strategy_classes']) > 1:
            axs3 = plt.subplot(plot_number + 5, sharex=axs1)
            plt.xlabel('Time (iterations)')
            plt.ylabel('Strategy Count')
            plt.title('Strategy Count Over Time')
            for s in range(0, len(self.def_strategy_count)):
                for counter, p in enumerate(self.def_strategy_count[s]):
                    plt.plot(self.def_strategy_count[s][p], c=colors[counter], label=p.__name__)

            plt.plot([0] * len(self.defender_benefit), 'r--')
            plt.plot([self.defender_ea_properties['number_of_players']] * len(self.defender_benefit), 'r--')
            plt.legend()

        else:
            plot_number = plot_number - 2

        axs4 = plt.subplot(plot_number + 7, sharex=axs1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Payoff')
        plt.title('Defender\'s Payoff Over Time')
        defender_benefit_mean = np.mean(self.defender_benefit, axis=1)
        plt.plot(defender_benefit_mean, 'b')
        # plt.plot([def_reward] * len(self.defender_benefit), 'b')

        if len(self.defender_ea_properties['strategy_classes']) > 1 \
            or len(self.attacker_ea_properties['strategy_classes']) > 1:

            plot_number = 420
        else:
            plot_number = 320

        axs5 = plt.subplot(plot_number + 2, sharex=axs1, sharey=axs1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Average Rate Over Time')
        # TODO This needs to be average of the average
        for s in range(0, len(self.attacker_population)):
            m = np.mean(self.attacker_population[s][:, 0:self.att_keep_number], axis=1)
            mean_of_mean = [np.mean(m[:c + 1]) for c, t in enumerate(m)]
            plt.plot(mean_of_mean, c=colors[s])
            # plt.plot([att_equilibrium[s]] * len(self.attacker_population[s]), c=colors[s])

        axs6 = plt.subplot(plot_number + 4, sharex=axs1, sharey=axs2)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Rate')
        plt.title('Attacker\'s Rate Over Time')
        for s in range(0, len(self.attacker_population)):
            m = np.mean(self.attacker_population[s][:, 0:self.att_keep_number], axis=1)
            plt.plot(m, c=colors[s])
            # plt.plot([att_equilibrium[s]] * len(self.attacker_population[s]), c=colors[s])

        if len(self.attacker_ea_properties['strategy_classes']) > 1:
            axs7 = plt.subplot(plot_number + 6, sharex=axs1, sharey=axs3)
            plt.xlabel('Time (iterations)')
            plt.ylabel('Strategy Count')
            plt.title('Strategy Count Over Time')
            for s in range(0, len(self.att_strategy_count)):
                for counter, p in enumerate(self.att_strategy_count[s]):
                    plt.plot(self.att_strategy_count[s][p], c=colors[counter], label=p.__name__)
            plt.plot([0] * len(self.attacker_benefit), 'r--')
            plt.plot([self.attacker_ea_properties['number_of_players']] * len(self.attacker_benefit), 'r--')
            plt.legend()
        else:
            plot_number = plot_number - 2

        axs8 = plt.subplot(plot_number + 8, sharex=axs1, sharey=axs4)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Payoff')
        plt.title('Attacker\'s Payoff Over Time')
        attacker_benefit_mean = np.mean(self.attacker_benefit, axis=1)
        plt.plot(attacker_benefit_mean, 'r')
        # plt.plot([att_reward] * len(self.attacker_benefit), 'r')

        plt.xlim(start_time, end_time)

        fig.tight_layout()
        plt.show()

    def plot_variance_stats(self, start_time: float = 0, end_time: float = 0) -> None:

        if end_time == 0:
            end_time = len(self.defender_benefit)
        fig = plt.figure(figsize=(15, 4))

        axs1 = plt.subplot(121)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Defender Statistics ')
        plt.title('Defender\'s Statistics Over Time')
        for s in range(0, len(self.defender_population)):
            plt.plot(np.max(self.defender_population[s], axis=1)
                     - np.min(self.defender_population[s], axis=1), 'b', label='Max - Min')
            plt.plot(np.mean(self.defender_population[s], axis=1), 'r', label='Population Mean')
            plt.plot(np.std(self.defender_population[s], axis=1), 'g--', label='Standard Deviation')

            # plt.plot(self.defender_variation_stats[s]['mean_std'], 'b', label='100 MA Std')
            # plt.plot(self.defender_variation_stats[s]['max'], 'r')
            # plt.plot(self.defender_variation_stats[s]['min'], 'r')

        plt.legend()

        axs2 = plt.subplot(122, sharex=axs1)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Attacker Statistics ')
        plt.title('Attacker\'s Statistics Over Time')
        for s in range(0, len(self.attacker_population)):
            plt.plot(np.max(self.attacker_population[s], axis=1)
                     - np.min(self.attacker_population[s], axis=1), 'b', label='Max - Min')
            plt.plot(np.mean(self.attacker_population[s], axis=1), 'r', label='Population Mean')
            plt.plot(np.std(self.attacker_population[s], axis=1), 'g--', label='Standard Deviation')
            # plt.plot(self.defender_variation_stats[s]['max'], 'r')
            # plt.plot(self.defender_variation_stats[s]['min'], 'r')

        plt.legend()

        plt.xlim(start_time, end_time)

        fig.tight_layout()
        plt.show()


    def plot_strategy_count(self, start_time: float = 0, end_time: float = 0) -> None:

        if end_time == 0:
            end_time = len(self.defender_benefit)
        fig = plt.figure(figsize=(10, 8))

        axs3 = plt.subplot(211)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Strategy Count')
        plt.title('Defender Strategy Count Over Time')
        plt.plot([0] * len(self.defender_benefit), 'r--')
        plt.plot([self.defender_ea_properties['number_of_players']] * len(self.defender_benefit), 'r--')
        for s in range(0, len(self.def_strategy_count)):
            for counter, p in enumerate(self.def_strategy_count[s]):
                plt.plot(self.def_strategy_count[s][p], c=colors[counter], label=p.__name__)
        plt.legend()

        axs7 = plt.subplot(212, sharex=axs3)
        plt.xlabel('Time (iterations)')
        plt.ylabel('Strategy Count')
        plt.title('Attacker Strategy Count Over Time')
        plt.plot([0] * len(self.attacker_benefit), 'r--')
        plt.plot([self.attacker_ea_properties['number_of_players']] * len(self.attacker_benefit), 'r--')
        for s in range(0, len(self.att_strategy_count)):
            for counter, p in enumerate(self.att_strategy_count[s]):
                plt.plot(self.att_strategy_count[s][p], c=colors[counter], label=p.__name__)

        plt.legend()

        plt.xlim(start_time, end_time)

        fig.tight_layout()
        plt.show()

    def write_to_file(self, file_number: str = "-1") -> None:

        self.create_directory(self.ea_properties.get('file_location'))

        file = Path(self.ea_properties.get('file_location') + 'defender_generation_population_' + str(file_number)
                    + ".pkl")
        save_object(obj=self.defender_population, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'attacker_generation_population_' + str(file_number)
                    + ".pkl")
        save_object(obj=self.attacker_population, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'defender_payoffs_' + str(file_number) + ".pkl")
        save_object(obj=self.defender_benefit, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'attacker_payoffs_' + str(file_number) + ".pkl")
        save_object(obj=self.attacker_benefit, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'last_defender_strategies_' + str(file_number) + ".pkl")
        save_object(obj=self.defenders, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'last_attacker_strategies_' + str(file_number) + ".pkl")
        save_object(obj=self.attackers, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'defender_strategy_count_' + str(file_number) + ".pkl")
        save_object(obj=self.def_strategy_count, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'attacker_strategy_count_' + str(file_number) + ".pkl")
        save_object(obj=self.att_strategy_count, filename=file)

    def create_directory(self, directory: str) -> None:

        if not os.path.exists(directory):
            os.makedirs(directory)

    def write_info_files(self) -> None:
        self.create_directory(self.ea_properties.get('file_location') + 'info_files/')

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'ea_properties' + ".pkl")
        save_object(obj=self.ea_properties, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'tournament_properties' + ".pkl")
        save_object(obj=self.tournament_properties, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'defender_ea_properties' + ".pkl")
        save_object(obj=self.defender_ea_properties, filename=file)

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'attacker_ea_properties' + ".pkl")
        save_object(obj=self.attacker_ea_properties, filename=file)

    def read_from_file(self, file_number: (str | None) = None) -> None:

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'ea_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.ea_properties = pickle.load(put)

        # print(self.ea_properties['file_location'])
        self.ea_properties['file_location'] = "genetic_algorithms/" + self.ea_properties['file_location']

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'tournament_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.tournament_properties = pickle.load(put)

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'defender_ea_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.defender_ea_properties = pickle.load(put)

        self.number_of_servers = len(self.defender_ea_properties['move_costs'])

        file = Path(self.ea_properties.get('file_location') + 'info_files/' + 'attacker_ea_properties' + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.attacker_ea_properties = pickle.load(put)

        directory = os.fsencode(self.ea_properties.get('file_location'))

        # Find the latest file_number in the folder
        if file_number is None:
            max_value = -1
            for file in os.listdir(directory):
                filename = os.fsdecode(file)
                if filename.startswith("defender_generation_population_"):
                    v = int(filename.split("_")[-1].split(".")[0])
                    max_value = max(max_value, v)

            file_number = str(max_value)

        file = Path(self.ea_properties.get('file_location') + 'defender_generation_population_' + str(file_number)
                    + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.defender_population = pickle.load(put)

        file = Path(self.ea_properties.get('file_location') + 'attacker_generation_population_' + str(file_number)
                    + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.attacker_population = pickle.load(put)

        file = Path(self.ea_properties.get('file_location') + 'defender_payoffs_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.defender_benefit = pickle.load(put)

        file = Path(self.ea_properties.get('file_location') + 'attacker_payoffs_' + str(file_number) + ".pkl")
        if file.exists():
            with open(file, 'rb') as put:
                self.attacker_benefit = pickle.load(put)

        file = Path(self.ea_properties.get('file_location') + 'last_defender_strategies_' + str(file_number) + ".pkl")
        with open(file, 'rb') as put:
            self.defenders = pickle.load(put)

        file = Path(self.ea_properties.get('file_location') + 'last_attacker_strategies_' + str(file_number) + ".pkl")
        with open(file, 'rb') as put:
            self.attackers = pickle.load(put)

        file = Path(
            self.ea_properties.get('file_location') + 'defender_strategy_count_' + str(file_number) + ".pkl")
        with open(file, 'rb') as put:
            self.def_strategy_count = pickle.load(put)

        file = Path(
            self.ea_properties.get('file_location') + 'attacker_strategy_count_' + str(file_number) + ".pkl")
        with open(file, 'rb') as put:
            self.att_strategy_count = pickle.load(put)


def save_object(obj, filename: Path) -> None:
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def plot_universes(location: str, number: int) -> None:

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
