from typing import Tuple, Dict

from system import System
# If threshold is false, we assume attackers must get into whole system for benefit and defender has benefit whenever
# they are in control of one or more servers
from graphics.multi_player_animate import Animate
from strategies.player import Player
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.lm_periodic import LastMove

import numpy as np

from copy import copy

#
# from graphics.multi_player_animate import Animate

base_properties = {
    'time_limit': 1000,
}


class Game:
    """
      Representing the FlipIt/FlipThem/Threshold FlipThem Game, depending on the
      number of servers in the system and the threshold of the players.

      Holds a system and multiple players.
    """

    def __init__(
        self,
        players: Tuple[Player, ...],
        system: System,
        game_properties: Dict = base_properties,
    ):
        """

        :param players: A list/tuple of players to take part in the game
        :param system: System object containing a number of Server classes
        :param game_properties: A dictionary containing the properties of the game to be played
        """


        self.current_time: float = 0.0
        self.time_limit: float = game_properties['time_limit']
        self.players: Tuple[Player, ...] = players
        self.__system: System = system
        self.game_properties: Dict = game_properties
        self.__system.initialise_system(players, game_properties)

        for player in players:
            player.initialise_strategies(self.__system)

    def play(self) -> None:
        """
        Plays the prescribed game between the players \n
        """

        player_move_times = {player: player.check_for_move_times(self.game_properties, self.__system,
                                                                 self.current_time) for player in self.players}
        while self.current_time < self.time_limit:
            # Need to iterate through the player move times, for each server, and see which one goes first
            lowest_move_time_for_each_player = {}
            for player, times in player_move_times.items():
                lowest_move_time_for_each_player[player] = (min(times, key=times.get), times[min(times,
                                                                                                 key=times.get)])

            # Find the player with the soonest move time
            next_player_to_move = min(lowest_move_time_for_each_player,
                                      key=lambda k: lowest_move_time_for_each_player[k][1])

            # Create 2-tuple of player and 2-tuple of server and move time
            player_move = (next_player_to_move, lowest_move_time_for_each_player[next_player_to_move])

            if player_move[1][1] < self.current_time:
                raise ValueError('Your player cheated, cannot move in the past')

            if player_move[1][1] < self.time_limit:

                # Now update the time
                self.current_time = player_move[1][1]
                # and give control of the resource to this player
                self.__system.change_server_control(player_move[1][0], player_move[0], self.current_time)

                player_move_times.pop(player_move[0], None)

                player_move_times[player_move[0]] = player_move[0].check_for_move_times(self.game_properties,
                                                                                        self.__system,
                                                                                        self.current_time)
                # A move has taken place, we need to check the whole system for ownership of each server and
                # then check what full system benefit needs to be applied.

            else:
                self.current_time = self.time_limit
                for server in self.__system.get_all_servers():
                    self.__system.change_server_control(server, server.get_current_controller(), self.current_time)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                                         #
    #                   Getters                               #
    #                                                         #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # def get_players(self) -> Player:
    #     return self.players

    def get_system(self):
        """
        :return: System the game is played over
        """
        return self.__system

    def get_time_limit(self) -> float:
        """
        :return: The time limit of the game
        """
        return self.game_properties['time_limit']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                                         #
    #                   Reset Methods                         #
    #                                                         #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def reset(self) -> None:
        """
        Resets the system ready for a new game. \n
        Resets the time to zero. \n
        """
        self.__system.reset_system()
        self.current_time = 0.0

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                                         #
    #                   Prints outs                           #
    #                                                         #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def print_individual_server_summary(self) -> None:
        """
        Prints server summary for each player \n
        """
        for server in self.__system.get_all_servers():
            total_time = 0
            print("==========", server.get_name(), "==========")
            for player in server.get_players():
                print(player.get_name())
                total_time += server.get_benefit_value(player, self.time_limit)
                print("       Gain value: ", server.get_benefit_value(player, self.time_limit))
                print("       Number of moves: ", server.get_number_of_moves(player, self.time_limit))
                print("       Overall Benefit", server.get_reward_for_player(player, self.time_limit))
                print("       Overall Benefit", server.get_player_benefit_times(player))
                print("       ---------------")
            print("Total time:", total_time)
            print("-----------------------------------------------")

    def print_full_game_summary(self) -> None:
        """
        Prints the results of the full system/game \n
        """
        print("------- System benefit --------")
        for player in self.players:
            print(player.get_name(), self.__system.get_system_gain_times(player))
            print(player.get_name(), self.__system.get_system_reward(player))

        print("----------------------------------------------------------")


if __name__ == '__main__':

    # defender_properties = {'move_costs': (0.6, 0.4, 0.3),
    #                        'threshold': 2
    #                        }
    # attacker_properties = {'move_costs': (0.3, 0.3, 0.2),
    #                        'threshold': 2
    #                        }

    # game_properties = {'time_limit': 5}
    #
    # defender = Player("Defender ", player_properties=copy(defender_properties),
    #                   strategies=(Periodic(0.5), Periodic(0.8), Periodic(0.3)))
    # attacker = Player("Attacker ",
    #                   player_properties=copy(attacker_properties),
    #                   strategies=(Periodic(0.7), Periodic(0.8), Periodic(0.7)))
    # s = System(3)

    defender_properties = {'move_costs': (0.6,),
                           'threshold': 1
                           }
    attacker_properties = {'move_costs': (0.3,),
                           'threshold': 1
                           }

    game_properties = {'time_limit': 5}

    defender = Player("Defender ", player_properties=copy(defender_properties),
                      strategies=(Exponential(1.0),))
    attacker = Player("Attacker ",
                      player_properties=copy(attacker_properties),
                      strategies=(Exponential(1.0),))
    s = System(1)



    g = Game(players=(defender, attacker), system=s, game_properties=game_properties)

    g.play()

    #
    a = Animate()

    g.print_full_game_summary()
    a.start(g)

