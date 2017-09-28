from game import Game
from system import System
import numpy as np
import time

from game import Game
from enum import Enum


example_tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.5
}

def defenders_reward(rates, costs):
    gain = 1 - rates[1]/(rates[1] + rates[0])

    cost = rates[0] * costs[0]

    return gain - cost


def attackers_reward(rates, costs):
    gain = rates[1] / (rates[1] + rates[0])

    cost = rates[1] * costs[1]

    return gain - cost


class Tournament(object):
    """
    Takes in any number of strategies, puts each one in the defending position and plays them against the whole population
    of attackers in order to see which is the strongest.
    - Need to set up exactly the same game each time: Time_limit etc.
    - Decide on number of times we play each game
    - Best way to record all results. (Writing to text files, retrieving these files and using Pandas to analyse the data)
    """

    def __init__(self, defender_strategies, attacker_strategies, tournament_properties):
        """
        :param player_strategies: a tuple of players with different (or the same strategies)
        :param game_properties: game properties to be played throughout the tournament
        """
        # Needs to iterate through each strategy, putting them as defence
        # Then iterate through the rest of the strategies in attacking position
        #
        self.attacker_strategies = attacker_strategies
        self.defender_strategies = defender_strategies
        self.tournament_properties = tournament_properties
        self.defender_results = {}
        self.attacker_results = {}
        self.mean_defender_results = {}
        self.mean_attacker_results = {}


        for attacker in self.attacker_strategies:
            self.attacker_results[attacker] = {}
            self.mean_attacker_results[attacker] = {}

        for defender in self.defender_strategies:
            self.defender_results[defender] = {}
            self.mean_defender_results[defender] = {}

    def play_tournament(self):

        total_games = len(self.attacker_strategies) * len(self.defender_strategies)
        games_to_play = total_games * self.tournament_properties['selection_ratio']

        for match in range(0, int(games_to_play)):

            correct_choice = False
            while not correct_choice:
                defender = np.random.choice(self.defender_strategies)
                attacker = np.random.choice(self.attacker_strategies)

                if self.defender_results.get(defender).get(attacker) is None:
                    self.defender_results[defender][attacker] = []
                    self.attacker_results[attacker][defender] = []
                    correct_choice = True

            for i in range(0, self.tournament_properties['number_of_rounds']):
                defender_rate = defender.get_strategies()[0].get_rate()
                attacker_rate = attacker.get_strategies()[0].get_rate()

                defender_cost = defender.get_player_properties()['move_costs'][0]
                attacker_cost = attacker.get_player_properties()['move_costs'][0]

                self.defender_results[defender][attacker].append((defenders_reward((defender_rate, attacker_rate),
                                                                                   (defender_cost, attacker_cost)),
                                                                  attackers_reward((defender_rate, attacker_rate),
                                                                                   (defender_cost, attacker_cost))))

                self.attacker_results[attacker][defender].append((attackers_reward((defender_rate, attacker_rate),
                                                                                   (defender_cost, attacker_cost)),
                                                                  defenders_reward((defender_rate, attacker_rate),
                                                                                   (defender_cost, attacker_cost))))
            # Need to calculate the mean of the results for each playoff
            self.mean_defender_results[defender][attacker] = (
            np.mean([x[0] for x in self.defender_results[defender][attacker]]),
            np.mean([x[1] for x in self.defender_results[defender][attacker]]))

            self.mean_attacker_results[attacker][defender] = (
            np.mean([x[0] for x in self.attacker_results[attacker][defender]]),
            np.mean([x[1] for x in self.attacker_results[attacker][defender]]))


    def get_mean_defense(self):
        mean_defense = {}
        for defender in self.defender_strategies:
            mean_defense[defender] = np.mean([self.mean_defender_results[defender][x][0]
                                              for x in self.mean_defender_results[defender]])
        return mean_defense

    def get_mean_attack(self):
        mean_attack = {}
        for attacker in self.attacker_strategies:
            mean_attack[attacker] = np.mean([self.mean_attacker_results[attacker][x][0]
                                             for x in self.mean_attacker_results[attacker]])
        return mean_attack
