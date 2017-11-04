from game import Game
from system import System
import numpy as np
import time
import multiprocessing

from game import Game
from multiprocessing import Process, Queue

example_tournament_properties = {
    'number_of_rounds': 1,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 0.5
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


        for attacker in self.attacker_strategies:
            self.attacker_results[attacker] = {}
            self.mean_attacker_results[attacker] = {}

        for defender in self.defender_strategies:
            self.defender_results[defender] = {}
            self.mean_defender_results[defender] = {}


    def play_games(self, queue,  players):
        defender = players[0]
        defender.get_player_properties()['threshold'] = self.tournament_properties['defender_threshold']
        attacker = players[1]
        attacker.get_player_properties()['threshold'] = self.tournament_properties['attacker_threshold']

        if self.defender_results.get(defender).get(attacker) is None:
            self.defender_results[defender][attacker] = []
            self.attacker_results[attacker][defender] = []

        for i in range(0, self.tournament_properties['number_of_rounds']):
            g = Game((defender, attacker), self.system, self.game_properties)

            g.play()
            self.defender_results[defender][attacker].append((self.system.get_system_reward(defender),
                                                              self.system.get_system_reward(attacker)))

            self.attacker_results[attacker][defender].append((self.system.get_system_reward(attacker),
                                                              self.system.get_system_reward(defender)))
            g.reset()
            self.system = System(self.system.get_number_of_servers())

            queue.put(self.defender_results)

            # print("here")
            # print(self.defender_results[defender][attacker])

        # Need to calculate the mean of the results for each playoff
        self.mean_defender_results[defender][attacker] = (
            np.mean([x[0] for x in self.defender_results[defender][attacker]]),
            np.mean([x[1] for x in self.defender_results[defender][attacker]]))

        self.mean_attacker_results[attacker][defender] = (
            np.mean([x[0] for x in self.attacker_results[attacker][defender]]),
            np.mean([x[1] for x in self.attacker_results[attacker][defender]]))

        # print("MEAN: ", self.mean_defender_results[defender])
        # print("this")


    def play_tournament(self):

        total_games = len(self.attacker_strategies) * len(self.defender_strategies)
        games_to_play = total_games * self.tournament_properties['selection_ratio']

        game_set = set()

        while len(game_set) < games_to_play:

            game_set.add((np.random.choice(self.defender_strategies), np.random.choice(self.attacker_strategies)))

        procs = list()

        # pool = multiprocessing.Pool()
        # pool.map(self.play_games, game_set)
        queue = Queue()
        for game in game_set:
            p = Process(target=self.play_games, args=(queue, game))
            procs.append(p)
            p.start()

        for _ in procs:
            val = queue.get()
            print(val)

        # print("MEAN: ", self.mean_defender_results)
        # print("this")

        for p in procs:
            p.join()

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
