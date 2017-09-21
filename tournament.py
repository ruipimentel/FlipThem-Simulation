from game import Game
from system import System
import numpy as np
import time

from game import Game
from enum import Enum
from random import randint


class Selection(Enum):
    TOURNAMENT_SELECTION = 1
    SELECT_ALL = 2


example_tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection': Selection.SELECT_ALL
}


class Tournament(object):
    """
    Takes in any number of strategies, puts each one in the defending position and plays them against the whole population
    of attackers in order to see which is the strongest.
    - Need to set up exactly the same game each time: Time_limit etc.
    - Decide on number of times we play each game
    - Best way to record all results. (Writing to text files, retrieving these files and using Pandas to analyse the data)
    """

    def __init__(self, defender_strategies, attacker_strategies, system,  game_properties, tournament_properties):
        """
        :param player_strategies: a tuple of players with different (or the same strategies)
        :param game_properties: game properties to be played throughout the tournament
        """
        # Needs to iterate through each strategy, putting them as defence
        # Then iterate through the rest of the strategies in attacking position
        #
        self.attacker_strategies = attacker_strategies
        self.defender_strategies = defender_strategies
        self.game_properties = game_properties
        self.tournament_properties = tournament_properties
        self.system = system
        self.defender_results = {}
        self.attacker_results = {}
        self.mean_defender_results = {}
        self.mean_attacker_results = {}

        if tournament_properties.get('selection') is None:
            tournament_properties['selection'] = Selection.SELECT_ALL

    def play_tournament(self):

        for attacker in self.attacker_strategies:
            self.attacker_results[attacker] = {}
            self.mean_attacker_results[attacker] = {}

            for defender in self.defender_strategies:
                self.attacker_results[attacker][defender] = []

        for defender in self.defender_strategies:

            # Select the strategies that will play each other
            defender_vs_attacker_set = set()

            if self.tournament_properties.get('selection') == Selection.TOURNAMENT_SELECTION:
                if len(self.attacker_strategies) < 10:
                    raise Exception("You have less than 10 attacker strategies. Do not use Tournament Selection")

                number_of_matches = len(self.attacker_strategies) // 5

                while len(defender_vs_attacker_set) < number_of_matches:
                    defender_vs_attacker_set.add(self.attacker_strategies[randint(0, len(self.attacker_strategies)-1)])

            else:
                defender_vs_attacker_set = set(self.attacker_strategies)

            defender.get_player_properties()['threshold'] = self.tournament_properties['defender_threshold']
            self.defender_results[defender] = {}
            self.mean_defender_results[defender] = {}
            t = time.time()
            for attacker in defender_vs_attacker_set:
                attacker.get_player_properties()['threshold'] = self.tournament_properties['attacker_threshold']
                self.defender_results[defender][attacker] = []
                t = time.time()
                for i in range(0, self.tournament_properties['number_of_rounds']):

                    g = Game((defender, attacker), self.system, self.game_properties)

                    g.play()
                    self.defender_results[defender][attacker].append((self.system.get_system_reward(defender),
                                                                      self.system.get_system_reward(attacker)))

                    self.attacker_results[attacker][defender].append((self.system.get_system_reward(attacker),
                                                                      self.system.get_system_reward(defender)))
                    g.reset()
                    self.system = System(self.system.get_number_of_servers())

                # Need to calculate the mean of the results for each playoff
                self.mean_defender_results[defender][attacker] = (np.mean([x[0] for x in self.defender_results[defender][attacker]]),
                                                         np.mean([x[1] for x in self.defender_results[defender][attacker]]))

                self.mean_attacker_results[attacker][defender] = (np.mean([x[0] for x in self.attacker_results[attacker][defender]]),
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
