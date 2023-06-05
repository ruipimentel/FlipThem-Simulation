from __future__ import annotations

from typing import List, Dict, Tuple, TYPE_CHECKING

from core.server import Server

if TYPE_CHECKING:
    from strategies.player import Player


class System(object):
    """
        - Holds a list of servers for the Game class to manipulate
        - Based on the threshold, calculates the reward of each player
        - This is where the game type can be decided, all on the reward structure (threshold etc.) (?)
        - Gain: amount of time a player receives "something" from the system
        - Reward: Gain minus the cost of each move carried out
    """

    def __init__(self, number_of_servers: int):
        """
        :param number_of_servers: Number of servers in the system
        """
        self.__servers: List[Server] = []
        self.__player_benefits: Dict[Player, List[Tuple[float, float]]] = {}
        self.player_ownership_count: Dict[Player, int] = {}
        self.players: Tuple[Player, ...] = ()
        self.player_ownership: Dict[Player, bool] = {}
        self.game_properties: (Dict | None) = None
        self.number_of_servers: int = number_of_servers

        for i in range(0, self.number_of_servers):
                self.__servers.append(Server("Server " + str(i)))

        self.__servers = tuple(self.__servers)

    def initialise_system(self, players: Tuple[Player, ...], game_properties: (Dict | None) = None) -> None:

        self.players = players
        self.game_properties = game_properties

        for player in players:
            self.__player_benefits[player] = []
            if player == players[0]:
                self.player_ownership[player] = True
                self.__player_benefits[player].append((0.0, 0.0))
            else:
                self.player_ownership[player] = False

            self.player_ownership_count[player] = 0
        for counter, server in enumerate(self.__servers):
            server.initialise_server(players, game_properties, counter)

    def get_all_servers(self) -> List[Server]:
        return self.__servers

    def get_server_by_name(self, name) -> (Server | bool):
        for server in self.__servers:
            if server.get_name() == name:
                return server

        return False

    def get_number_of_servers(self) -> int:
        return len(self.__servers)

    def change_server_control(self, server: Server, player: Player, time: float) -> None:
        if isinstance(server, str):
            self.get_server_by_name(server).change_control(player, time)
        else:
            self.get_server_by_name(server.get_name()).change_control(player, time)

        server_control = {}
        for player in self.players:
            self.player_ownership_count[player] = 0

        # Go through each server
        for server in self.__servers:
            # Find current controller of all servers
            server_control[server] = server.get_current_controller()
            # player count
            self.player_ownership_count[server.get_current_controller()] += 1

        # We have the number of servers each player is in control of
        # Need to iterate through each player, and check with their respective servers
        for player in self.players:
            if self.player_ownership_count[player] >= player.get_player_properties()['threshold']:
                # This means the player should be gaining system benefit
                # Check whether player is already receiving benefit
                if self.player_ownership[player]:
                    t = self.__player_benefits[player][-1]
                    self.__player_benefits[player][-1] = (t[0], time)
                else:
                    self.player_ownership[player] = True
                    self.__player_benefits[player].append((time, time))
            else:
                # This means that player isn't gaining benefit now, or never was
                if self.player_ownership[player]:
                    t = self.__player_benefits[player][-1]
                    self.__player_benefits[player][-1] = (t[0], time)
                    self.player_ownership[player] = False

    def get_player_server_benefits(self, player: Player, server: Server) -> float:
        return self.get_server_by_name(server.get_name()).get_benefit_value(player)

    def get_system_gain_times(self, player: Player, time: (float | None) = None) -> List[Tuple[float, float]]:
        if time is None:
            return self.__player_benefits[player]
        elif self.__player_benefits.get(player) is not None:
            return [move for move in self.__player_benefits.get(player) if move <= time]
        else:
            return []

    def get_all_player_benefit_times(self) -> Dict[Player, List[Tuple[float, float]]]:
        return self.__player_benefits

    def get_system_reward(self, player, time: (float | None) = None) -> float:

        if time == 0:
            return 0

        benefit_history = self.get_system_gain_times(player, time)
        benefit = 0
        for t in benefit_history:
            benefit += t[1] - t[0]

        for server in self.get_all_servers():
            number_of_moves = server.get_number_of_moves(player)
            cost = server.get_player_costs(player)
            benefit -= (number_of_moves * cost)

        return benefit/self.__get_latest_time()

    def get_players(self) -> Tuple[Player, ...]:
        return self.players

    def reset_system(self) -> None:

        for server in self.get_all_servers():
            server.reset_server()

    def __get_latest_time(self) -> float:
        latest_move_time = 0.0

        for player in self.__player_benefits:
            benefit_history = self.get_system_gain_times(player)
            if len(benefit_history) > 0 and benefit_history[-1][1] > latest_move_time:
                latest_move_time = benefit_history[-1][1]

        return latest_move_time
