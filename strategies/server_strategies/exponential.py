from typing import Dict

import numpy as np
from strategies.server_strategies.server_strategy import ServerStrategy


class Exponential(ServerStrategy):
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

        :param information:
        :return:
        """
        return information['current_time'] + np.random.exponential(1/self.rate)

    def get_rate(self) -> float:
        return self.rate

    def __str__(self) -> str:
        return "Exponential " + str(self.rate)

    def age_density(self, z: float, rate: float) -> float:
        return rate * np.exp(-rate * z)

    def age_distribution(self, z: float, rate: float) -> float:
        return 1 - np.exp(-rate * z)

