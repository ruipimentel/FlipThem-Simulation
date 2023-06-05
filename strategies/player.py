from __future__ import annotations

from typing import Tuple, Dict, TYPE_CHECKING

import reward_functions.renewal as renewal
from strategies.server_strategies.periodic import Periodic

from strategies.server_strategies.server_strategy import ServerStrategy

if TYPE_CHECKING:
    from core.system import System
    from core.server import Server


base_properties = {
    'move_costs': (1.0,),
}


class Player:

    def __init__(
        self,
        name: str,
        strategies: (Tuple[ServerStrategy, ...] | ServerStrategy | None) = None,
        player_properties: Dict = base_properties,
    ):
        """

        :param name: Name of player
        :param player_properties: See base properties above
        :param strategies: Tuple of strategies that matches up to the servers. (ensure exact numbers)
        """

        self.__name: str = name
        # Setting player_properties
        if player_properties != base_properties:
            for prop in base_properties:
                if player_properties.get(prop) is None:
                    print("Missed player property: ", prop, "(Replacing with base_property)")
                    player_properties[prop] = base_properties[prop]
        self.player_properties: Dict = player_properties
        self.server_strategies: Dict[Server, ServerStrategy] = {}
        self.planned_moves: Dict[Server, float] = {}

        if isinstance(strategies, ServerStrategy):
            self.strategies: Tuple[ServerStrategy, ...] = (strategies,)
        else:
            self.strategies: (Tuple[ServerStrategy, ...] | None) = strategies

    def initialise_strategies(self, system: System) -> None:

        self.reset()

        if system.get_number_of_servers() != len(self.strategies):
            raise Exception("Number of player strategies does not equal number of servers")
        else:
            for counter, server in enumerate(system.get_all_servers()):
                self.server_strategies[server] = self.strategies[counter]

    def check_for_move_times(self, game_properties: Dict, system: System, current_time: float) -> Dict[Server, float]:
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

        # Calculates the next move times for all servers:
        if current_time == 0.0:
            for server in system.get_all_servers():
                information['server'] = server
                playing_times[server] = self.server_strategies.get(server).get_next_move_time(information)

            self.planned_moves = playing_times

            return playing_times

        # Locates the expired moves, then substitutes them by new move times:
        new_move = {server: time for server, time in self.planned_moves.items() if time <= current_time}
        playing_times = self.planned_moves
        for server in new_move.keys():
            information['server'] = server
            playing_times[server] = self.server_strategies.get(server).get_next_move_time(information)

        # This line below seems unnecessary, since we're already mutating
        # `self.planned_moves` when mutating `playing_times` above:
        self.planned_moves = playing_times

        return playing_times

    def reset(self) -> None:
        self.server_strategies = {}
        self.planned_moves = {}

    def get_name(self) -> str:
        return self.__name

    def set_name(self, name) -> None:
        self.__name = name

    def get_player_properties(self) -> Dict:
        return self.player_properties

    def update_strategy_rate(self, strategy_number, rate) -> None:
        temp_list = list(self.strategies)
        temp_list[strategy_number] = type(self.strategies[strategy_number])(rate)
        self.strategies = tuple(temp_list)

    def update_strategy(self, strategy_number, strategy) -> None:
        temp_list = list(self.strategies)
        temp_list[strategy_number] = strategy
        self.strategies = tuple(temp_list)

    def get_strategies(self) -> (Tuple[ServerStrategy, ...] | None):
        return self.strategies

    def get_strategy_rate(self, server_number: int) -> float:
        return self.strategies[server_number].get_rate()

    def get_strategy(self, server_number: int) -> ServerStrategy:
        return self.strategies[server_number]

    def set_strategies(self, strategies) -> None:
        self.strategies = strategies
