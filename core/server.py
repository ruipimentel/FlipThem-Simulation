from __future__ import annotations

from typing import Tuple, List, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from strategies.player import Player

class Server:
    """
    - Keeps record of who currently owns this resource \n
    - Keeps the complete move history of the resource for every player \n
    - Holds a dictionary move costs (this could be compromising (attacking), resetting (defending), peeking etc. \n
    - Keeps a dictionary of when each player was in control of the resource
    """

    def __init__(self, name: str):
        """
        :param name: String to signify the name of the server
        """
        self.__name: str = name
        self.__current_controller: (Player | None) = None
        self.__player_costs: Dict[Player, float] = {}  # Dictionary {Player: move_cost}

        self.__player_history: Dict[Player, List[float]] = {}  # Dictionary {Player: [move_times]}
        self.__player_benefits: Dict[Player, Tuple[float, float]] = {}  # Dictionary {Player: (Benefit start, Benefit end)}
        self.__player_costs: Dict[Player, float] = {}

    def initialise_server(self, players: Tuple[Player, ...], game_properties: (Dict | None) = None, server_number: int = 0) -> None:
        """
        :param players: list/tuple of players fighting over the server
        :param game_properties: Contains the properties for the game (currently not used here)
        :param server_number: The server number in the list of servers for the system
        """
        for player in players:

            self.__player_history[player] = []
            self.__player_benefits[player] = []
            if server_number < len(player.get_player_properties()['move_costs']):
                self.__player_costs[player] = player.get_player_properties()['move_costs'][server_number]
            else:
                print(server_number, player.get_player_properties()['move_costs'])
                raise Exception("Not enough player move costs", player.get_name(), self.get_name())
        # TODO: for now, assume the first player controls it
        self.__current_controller = players[0]

    def change_control(self, player: Player, current_time: float) -> None:
        """
        :param player: the player taking control of the server
        :param current_time: The time at which the player takes control
        """

        # Get the player currently controlling the server
        current_controller = self.__current_controller
        # Find how long they've controlled the server
        if len(self.__player_history[current_controller]) > 0:
            last_move = self.__player_history[current_controller][-1]
        else:
            last_move = 0.0
        # Update the benefit
        self.__update_player_benefits(current_controller, last_move, current_time)
        self.__current_controller = player
        self.__add_history(player, current_time)

    def __update_player_benefits(self, player: Player, last_move: float, current_time: float) -> None:
        """
        :param player: the player in question
        :param last_move: When they last moved
        :param current_time: The time right now
        """
        self.__player_benefits[player].append((last_move, current_time))

    def get_current_controller(self) -> (Player | None):
        """
        :return: The player currently in control of the server
        """
        return self.__current_controller

    def __add_history(self, player: Player, current_time: float) -> None:
        """
        :param player:
        :param current_time:
        """
        self.__player_history[player].append(current_time)

    def get_name(self) -> str:
        return self.__name

    def get_history(self, player: Player, time: (float | None) = None) -> List[float]:
        if time is None:
            return self.__player_history[player]
        elif self.__player_history.get(player) is not None:
            return [move for move in self.__player_history.get(player) if move <= time]

    def get_player_benefit_times(self, player: Player) -> Tuple[float, float]:
        return self.__player_benefits[player]

    def get_all_player_benefit_times(self) -> Dict[Player, Tuple[float, float]]:
        return self.__player_benefits

    def get_player_costs(self, player: Player) -> float:
        return self.__player_costs[player]

    def get_benefit_value(self, player: Player, time: float) -> float:
        benefit = 0
        benefit_history = self.get_player_benefit_times(player)
        times_we_include = [move for move in benefit_history if move[0] <= time]
        for t in times_we_include:
            if time > t[1]:
                benefit += t[1] - t[0]
            else:
                benefit += time - t[0]

        return benefit

    def get_players(self) -> List[Player]:

        return list(self.__player_history.keys())

    def get_number_of_moves(self, player: Player, time: (float | None) = None) -> int:
        return len(self.get_history(player, time))

    def get_reward_for_player(self, player: Player, time: float) -> float:
        absolute_reward = self.get_benefit_value(player, time) - \
                          self.get_number_of_moves(player, time) * self.__player_costs[player]
        return absolute_reward / time

    def reset_server(self) -> None:
        for player in self.__player_history:
            self.__player_history[player] = []
            self.__player_benefits[player] = []
            # TODO: for now, assume the first player controls it
            self.__current_controller = self.get_players()[0]
