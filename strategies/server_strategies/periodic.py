import numpy as np

from strategies.server_strategies.server_strategy import ServerStrategy


class Periodic(ServerStrategy):
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

        if current_time == 0:
            return np.random.uniform(0.0, 1/self.rate)

        else:
            return current_time + 1/self.rate

    def get_rate(self):
        return self.rate

    def __str__(self):
        return "Periodic " + str(self.rate)
