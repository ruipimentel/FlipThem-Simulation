from system import System
# If threshold is false, we assume attackers must get into whole system for benefit and defender has benefit whenever
# they are in control of one or more servers
#
# from strategies.player import Player
# from strategies.server_strategies.exponential import Exponential
# from strategies.server_strategies.periodic import Periodic
#
#
# from graphics.multi_player_animate import Animate

base_properties = {
        'time_limit': 1000
    }


class Game(object):
    """ Abstract class to represent a game played between two different players.
      Subclasses will be FlipIt, FlipThem, MultiRateFlipThem etc.

      This will contain the number of resources of type Resource included in the game.
      At any point in time we can view the number of resources each player is currently in control of.

    """

    def __init__(self, players, system, game_properties=base_properties):

        self.current_time = 0.0
        self.time_limit = game_properties['time_limit']
        self.players = players
        self.__system = system
        self.game_properties = game_properties
        self.__system.initialise_system(players, game_properties)

        for player in players:
            player.initialise_strategies(self.__system)

    def play(self):
        """ Game Method:
            Find when players will make their next move, order this.
            Whoever moves earliest games control, then calculate their next move time
            Game loops on this until time_limit.
        """

        player_move_times = {player: player.check_for_move_times(self.game_properties, self.__system,
                                                                 self.current_time) for player in self.players}
        while self.current_time < self.time_limit:
            # Need to iterate through the player move times, for each server, and see which one goes first...
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

    def get_system(self) -> System:
        return self.__system

    def get_time_limit(self):
        return self.game_properties['time_limit']

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                                         #
    #                   Reset Methods                         #
    #                                                         #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def reset(self):

        self.__system.reset_system()
        self.current_time = 0.0
        # TODO Reset player's values: history etc.

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    #                                                         #
    #                   Prints outs                           #
    #                                                         #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def print_individual_server_summary(self):
        """
        Prints server summary for each player
        :return: None
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
        print("------- System benefit --------")
        for player in self.players:
            print(player.get_name(), self.__system.get_system_gain_times(player))
            print(player.get_name(), self.__system.get_system_reward(player))

        print("----------------------------------------------------------")

#
# p1 = Player("Player 1 ", Exponential(0.6))
# p2 = Player("Player 2 ", strategies=Periodic(1))
#
# g = Game((p1, p2), System(1))
#
# g.play()
# g.print_full_game_summary()
#
# a = Animate()
#

# a.start(g)
