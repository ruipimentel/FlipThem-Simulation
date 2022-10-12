import numpy as np
from multiprocessing import Pool
from enum import Enum

from game import Game
from system import System
from reward_functions.renewal import reward

class TOURNAMENT_TYPE(Enum):
    STOCHASTIC = 1
    DETERMINISTIC = 2


class Tournament(object):
    """
    Takes in any number of strategies, puts each one in the defending position & play them against the whole population
    of attackers in order to see which is the strongest.
    - Need to set up exactly the same game each time: Time_limit etc.
    - Decide on number of times we play each game
    """

    def __init__(self, defender_strategies=None, attacker_strategies=None, tournament_properties=None):
        # Needs to iterate through each strategy, putting them as defence
        # Then iterate through the rest of the strategies in attacking position
        #
        self.attacker_strategies = attacker_strategies
        self.defender_strategies = defender_strategies
        self.tournament_properties = tournament_properties
        number_of_resources = len(attacker_strategies[0].get_strategies())
        self.system = System(number_of_resources)
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

    def play_games(self, players):
        system = System(self.system.get_number_of_servers())
        defender = players[0]
        defender.get_player_properties()['threshold'] = self.tournament_properties['defender_threshold']
        attacker = players[1]
        attacker.get_player_properties()['threshold'] = self.tournament_properties['attacker_threshold']

        defender_results = []
        attacker_results = []

        if self.tournament_properties['tournament_type'] is TOURNAMENT_TYPE.STOCHASTIC:
            for i in range(0, self.tournament_properties['number_of_rounds']):

                g = Game((defender, attacker), system, self.tournament_properties['game_properties'])

                g.play()
                defender_results.append((system.get_system_reward(defender), system.get_system_reward(attacker)))
                attacker_results.append((system.get_system_reward(attacker), system.get_system_reward(defender)))

                g.reset()
        elif self.tournament_properties['tournament_type'] is TOURNAMENT_TYPE.DETERMINISTIC:
            defender_rates = [s.get_rate() for s in defender.get_strategies()]
            attacker_rates = [s.get_rate() for s in attacker.get_strategies()]

            defender_functions = ([s.age_density for s in defender.get_strategies()],
                                  [s.age_distribution for s in defender.get_strategies()])

            attacker_functions = ([s.age_density for s in attacker.get_strategies()],
                                  [s.age_distribution for s in attacker.get_strategies()])


            defender_costs = defender.get_player_properties()['move_costs']
            attacker_costs = attacker.get_player_properties()['move_costs']

            threshold = self.tournament_properties['attacker_threshold']
            defenders_reward, attackers_reward = reward(threshold, defender_functions, attacker_functions,
                                                        defender_rates, attacker_rates, defender_costs,
                                                        attacker_costs)

            defender_results.append((defenders_reward, attackers_reward))
            attacker_results.append((attackers_reward, defenders_reward))

        return defender_results, attacker_results

    def play_tournament(self):

        total_games = len(self.attacker_strategies) * len(self.defender_strategies)
        games_to_play = total_games * self.tournament_properties['selection_ratio']

        game_set = set()

        while len(game_set) < games_to_play:

            game_set.add((np.random.choice(self.defender_strategies), np.random.choice(self.attacker_strategies)))

        with Pool() as p:
            results = p.map(self.play_games, game_set)

        for counter, match in enumerate(game_set):
            defender = match[0]
            attacker = match[1]

            self.defender_results[defender][attacker] = results[counter][0]
            self.attacker_results[attacker][defender] = results[counter][1]

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
