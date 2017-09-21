import numpy as np

from strategies.server_strategies.periodic import Periodic


class PhasePeriodic(Periodic):
    """
    This is a class that gets allocated by a Player class to a particular server.
    Need to decide how best to call the 'Check for next move' method.
    """

    def __init__(self, rate):
        """
        :param rate: 1 / period
        """
        Periodic.__init__(self, rate)
        self.phase_number = 2
        self.number_of_moves = 0

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
            self.number_of_moves += 1
            if self.number_of_moves == self.phase_number ** 2:
                self.phase_number += 1
                return current_time + np.random.uniform(0, 1 / self.rate)

            else:
                return current_time + 1/self.rate

    def get_rate(self):
        return self.rate

    def __str__(self):
        return "Phase Periodic " + str(self.rate)
