from system import System
import reward_functions.renewal as renewal
from strategies.server_strategies.periodic import Periodic

from strategies.server_strategies.server_strategy import ServerStrategy


base_properties = {
    'move_costs': (1.0,),
}


class Player:

    def __init__(self, name, strategies=None, player_properties=base_properties):
        """

        :param name: Name of player
        :param player_properties: See base properties above
        :param strategies: Tuple of strategies that matches up to the servers. (ensure exact numbers)
        """

        self.__name = name
        # Setting player_properties
        if player_properties != base_properties:
            for prop in base_properties:
                if player_properties.get(prop) is None:
                    print("Missed player property: ", prop, "(Replacing with base_property)")
                    player_properties[prop] = base_properties[prop]
        self.player_properties = player_properties
        self.server_strategies = {}
        self.planned_moves = {}

        if isinstance(strategies, ServerStrategy):
            self.strategies = (strategies,)
        else:
            self.strategies = strategies

    def initialise_strategies(self, system):

        self.reset()

        if system.get_number_of_servers() != len(self.strategies):
            raise Exception("Number of player strategies does not equal number of servers")
        else:
            for counter, server in enumerate(system.get_all_servers()):
                self.server_strategies[server] = self.strategies[counter]

    def check_for_move_times(self, game_properties, system, current_time):
        """
        :param game_properties:
         :param system: The grouping of servers, the player can use this API to find any information he is
            allowed to access
        :param current_time: Time of the game
        :return: Returns a dictionary of rates for each server
        """

        # Need to go through all the player properties, make it as generic as possible (if possible!)
        # For now, go through each server and find new move times
        # Check the time and see if the individual server strategies have been allocated to each server.
        playing_times = {}
        information = {'game_properties': game_properties,
                       'system': system,
                       'current_time': current_time,
                       'who_am_i': self}
        if current_time == 0.0:
            for server in system.get_all_servers():
                information['server'] = server
                playing_times[server] = self.server_strategies.get(server).get_next_move_time(information)

            self.planned_moves = playing_times

            return playing_times

        # Have to find the server, and only update that one, keep the rest as the same using planned_moves
        new_move = {server: time for server, time in self.planned_moves.items() if time <= current_time}
        playing_times = self.planned_moves
        for server in new_move.keys():
            information['server'] = server
            playing_times[server] = self.server_strategies.get(server).get_next_move_time(information)

        self.planned_moves = playing_times

        return playing_times

    def reset(self):
        self.server_strategies = {}
        self.planned_moves = {}

    def get_name(self):
        return self.__name

    def set_name(self, name):
        self.__name = name

    def get_player_properties(self):
        return self.player_properties

    def update_strategy_rate(self, strategy_number, rate):
        temp_list = list(self.strategies)
        temp_list[strategy_number] = type(self.strategies[strategy_number])(rate)
        self.strategies = tuple(temp_list)

    def update_strategy(self, strategy_number, strategy):
        temp_list = list(self.strategies)
        temp_list[strategy_number] = strategy
        self.strategies = tuple(temp_list)

    def get_strategies(self):
        return self.strategies

    def get_strategy_rate(self, server_number):
        return self.strategies[server_number].get_rate()

    def get_strategy(self, server_number):
        return self.strategies[server_number]

    def set_strategies(self, strategies):
        self.strategies = strategies