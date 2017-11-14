import numpy as np
from strategies.server_strategies.server_strategy import ServerStrategy


class Exponential(ServerStrategy):
    """
        This is a class that gets allocated by a Player class to a particular server.
        Need to decide how best to call the 'Check for next move' method.
        """

    def __init__(self, rate):
        """
        :param rate: 1 / period
        """
        self.rate = rate

    def get_next_move_time(self, game_properties, system, current_time):
        """
        :param game_properties:
        :param system:
        :param current_time: Time of the game
        :return: Returns the next move time
        """
        return current_time + np.random.exponential(1/self.rate)

    def get_rate(self):
        return self.rate

    def __str__(self):
        return "Exponential " + str(self.rate)
