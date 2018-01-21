# from strategies.player import Player

class Server:
    """
    - Keeps record of who currently owns this resource \n
    - Keeps the complete move history of the resource for every player \n
    - Holds a dictionary move costs (this could be compromising (attacking), resetting (defending), peeking etc. \n
    - Keeps a dictionary of when each player was in control of the resource
    """

    def __init__(self, name):
        """
        :param name: String to signify the name of the server
        :type name: str
        """
        self.__name = name
        self.__current_controller = None
        self.__player_costs = {}  # Dictionary {Player: move_cost}

        self.__player_history = {}  # Dictionary {Player: [move_times]}
        self.__player_benefits = {}  # Dictionary {Player: (Benefit start, Benefit end)}
        self.__player_costs = {}

    def initialise_server(self, players, game_properties=None, server_number=0) -> None:
        """
        :param players: list/tuple of players fighting over the server
        :type players: tuple of Player
        :param game_properties: Contains the properties for the game (currently not used here)
        :type game_properties: dict
        :param server_number: The server number in the list of servers for the system
        :type server_number: int
        :return: None
        :rtype: None
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

    def change_control(self, player, current_time) -> None:
        """
        :param player: the player taking control of the server
        :type player: Player
        :param current_time: The time at which the player takes control
        :type current_time: float
        :return: None
        :rtype: None
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

    def __update_player_benefits(self, player, last_move, current_time) -> None:
        """

        :param player: the player in question
        :type player: Player
        :param last_move: When they last moved
        :type last_move: float
        :param current_time: The time right now
        :type current_time: float
        :return:
        :rtype:
        """
        self.__player_benefits[player].append((last_move, current_time))

    def get_current_controller(self):
        """
        :return: The player currently in control of the server
        :rtype: Player
        """
        return self.__current_controller

    def __add_history(self, player, current_time) -> None:
        """
        :param player:
        :type player:
        :param current_time:
        :type current_time:
        :return:
        :rtype:
        """
        self.__player_history[player].append(current_time)

    def get_name(self):
        return self.__name

    def get_history(self, player, time=None):
        if time is None:
            return self.__player_history[player]
        elif self.__player_history.get(player) is not None:
            return [move for move in self.__player_history.get(player) if move <= time]

    def get_player_benefit_times(self, player):
        return self.__player_benefits[player]

    def get_all_player_benefit_times(self):
        return self.__player_benefits

    def get_player_costs(self, player):
        return self.__player_costs[player]

    def get_benefit_value(self, player, time):
        benefit = 0
        benefit_history = self.get_player_benefit_times(player)
        times_we_include = [move for move in benefit_history if move[0] <= time]
        for t in times_we_include:
            if time > t[1]:
                benefit += t[1] - t[0]
            else:
                benefit += time - t[0]

        return benefit

    def get_players(self):

        return list(self.__player_history.keys())

    def get_number_of_moves(self, player, time=None):
        return len(self.get_history(player, time))

    def get_reward_for_player(self, player, time):
        absolute_reward = self.get_benefit_value(player, time) - \
                          self.get_number_of_moves(player, time) * self.__player_costs[player]
        return absolute_reward / time

    def reset_server(self):
        for player in self.__player_history:
            self.__player_history[player] = []
            self.__player_benefits[player] = []
            # TODO: for now, assume the first player controls it
            self.__current_controller = self.get_players()[0]
