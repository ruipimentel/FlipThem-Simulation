from typing import Dict

import numpy as np

from strategies.server_strategies.server_strategy import ServerStrategy


class LastMove(ServerStrategy):
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
        if information['current_time'] == 0:
            return np.random.uniform(0.0, 1/self.rate)

        else:
            # Need to find when the player last moved.
            server = information['server']

            players = server.get_players()
            if len(players) == 2:
                # Check the length of the list is 2, i.e. just 2 players
                players.remove(information['who_am_i'])
                opponent = players[0]
                opponent_move_times = server.get_history(opponent)
                if len(opponent_move_times) >= 2:
                    opponent_rate = opponent_move_times[-1] - opponent_move_times[-2]

                    my_move_time = opponent_move_times[-1] + opponent_rate + 0.01
                    if my_move_time <= information['current_time']:
                        return information['current_time'] + opponent_rate
                    else:
                        return my_move_time
                else:
                    return information['current_time'] + np.random.uniform(0.0, 1/self.rate)

            else:
                raise NotImplementedError("We have not implemented this strategy for more than 2 players")



    def get_rate(self) -> float:
        return self.rate

    def __str__(self) -> str:
        return "LastMove"
