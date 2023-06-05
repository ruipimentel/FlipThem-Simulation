from typing import Dict

import numpy as np

from strategies.server_strategies.server_strategy import ServerStrategy


class Periodic(ServerStrategy):
    """
    This is a class that gets allocated by a Player class to a particular server.
    Need to decide how best to call the 'Check for next move' method.
    """

    def __init__(self, rate: float):
        """
        :param rate: 1 / period
        """
        self.rate: float = rate

    def get_next_move_time(self, information: Dict) -> float:
        """
        :param game_properties:
        :param system:
        :param current_time: Time of the game
        :return: Returns the next move time
        """

        if information['current_time'] == 0:
            return np.random.uniform(0.0, 1/self.rate)

        else:
            return information['current_time'] + 1/self.rate

    def get_rate(self) -> float:
        return self.rate

    def __str__(self) -> str:
        return "Periodic " + str(self.rate)

    def age_density(self, z: float, rate: float) -> float:
        if z < 1 / rate:
            return rate
        else:
            return 0

    def age_distribution(self, z: float, rate: float) -> float:
        if z < 1 / rate:
            return rate * z
        else:
            return 1
