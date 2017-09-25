from tournament import Tournament
from system import System
from strategies.player import Player
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.periodic import Periodic
from copy import copy
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib import cm

base_attacker_properties = {
    'multi_rate': True,
    'rates': (0.01,),
    'keep_move_until_completed': True,
    'individual_move_costs': True,
    'move_costs': (0.2,),
    'threshold': 1
}

base_defender_properties = {
    'multi_rate': True,
    'rates': (0.01,),
    'keep_move_until_completed': True,
    'individual_move_costs': True,
    'move_costs': (0.2,),
    'threshold': 1
}



example_tournament_properties = {
    'number_of_rounds': 5,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 1.0
}

example_game_properties = {
    'time_limit': 1000.0
}


class Iterate:

    def __init__(self, defender, attacker, defender_range, attacker_range):

        self.defender = defender
        self.attacker = attacker
        self.defender_range = defender_range
        self.attacker_range = attacker_range
        self.defender_data = np.array([])
        self.attacker_data = np.array([])
        self.defender_steps = np.array([])
        self.attacker_steps = np.array([])


    def calculate_optimal_responses(self):

        optimal_defender_x = []
        optimal_defender_y = []

        optimal_attacker_x = []
        optimal_attacker_y = []

        for u in self.defender_steps:
            self.defender.get_player_properties()['rates'] = (u,)
            optimal_attacker_y.append(self.periodic_opt_response(self.attacker, self.defender))
            optimal_attacker_x.append(u)

        for l in self.attacker_steps:
            self.attacker.get_player_properties()['rates'] = (l,)

            optimal_defender_x.append(self.periodic_opt_response(self.defender, self.attacker))
            optimal_defender_y.append(l)

        return (optimal_defender_x, optimal_defender_y), (optimal_attacker_x, optimal_attacker_y)

    def start_iteration(self, increment_size):

        self.defender_steps = np.linspace(self.defender_range[0], self.defender_range[1],
                                          (self.defender_range[1] - self.defender_range[0]) / increment_size)

        self.attacker_steps = np.linspace(self.attacker_range[0], self.attacker_range[1],
                                          (self.attacker_range[1] - self.attacker_range[0]) / increment_size)

        defender_data = []
        attacker_data = []

        round = 0

        for u in self.defender_steps:
            self.defender.get_player_properties()['rates'] = (u,)

            defender_list = []
            attacker_list = []

            for l in self.attacker_steps:
                self.attacker.get_player_properties()['rates'] = (l,)

                round += 1

                t = Tournament(defender_strategies=(defender,), attacker_strategies=(attacker,),
                               system=System(1), game_properties=example_game_properties,
                               tournament_properties=example_tournament_properties)

                t.play_tournament()

                print("--------------", round, "--------------------")
                print(self.defender.get_player_properties()['rates'], self.defender.get_name(),
                      t.get_mean_defense()[self.defender])
                print(self.attacker.get_player_properties()['rates'], self.attacker.get_name(),
                      t.get_mean_attack()[self.attacker])

                defender_list.append(t.get_mean_defense()[self.defender])
                attacker_list.append(t.get_mean_attack()[self.attacker])

            defender_data.append(np.array(defender_list))
            attacker_data.append(np.array(attacker_list))

        self.defender_data = np.array(defender_data)
        self.attacker_data = np.array(attacker_data)

    def __plot(self):

        fig = plt.figure(figsize=(15, 5))

        axs1 = fig.add_subplot(121)

        plt.xlabel('Defender Rate')
        plt.ylabel('Attacker Rate')
        plt.title('Heat Plot for the Defender\'s payoff')

        axs2 = fig.add_subplot(122)

        plt.xlabel('Defender Rate')
        plt.ylabel('Attacker Rate')
        plt.title('Heat Plot for the Attacker\'s payoff')

        X, Y = np.meshgrid(self.defender_steps, self.attacker_steps, indexing='ij')

        np_defender_data = np.ma.masked_where(self.defender_data <= 0.0, self.defender_data)
        cdmap = cm.Blues

        np_attacker_data = np.ma.masked_where(self.attacker_data <= 0.0, self.attacker_data)
        camap = cm.Reds

        cdmap.set_bad(color='white')
        print("this")
        np_defender_data = np.ma.masked_where(np_defender_data <= 0.0, np_defender_data)
        print(np_defender_data)
        np_attacker_data = np.ma.masked_where(np_attacker_data <= 0.0, np_attacker_data)
        print(np_attacker_data)
        print("that")

        axs1.grid(b=True, which='major', color='black', linestyle='-')
        dcs = axs1.contourf(X, Y, np_defender_data, cmap=cdmap)
        fig.colorbar(dcs, ax=axs1, format="%.2f")

        x_star, y_star = self.calculate_periodic_equilibrium()

        optimal_defender, optimal_attacker = self.calculate_optimal_responses()

        opt_d_x = optimal_defender[0]
        opt_d_y = optimal_defender[1]

        opt_a_x = optimal_attacker[0]
        opt_a_y = optimal_attacker[1]

        print("opt d y", opt_d_y)

        # data_x = [x_star]
        # data_y = [y_star]
        # axs1.plot(data_x, data_y, 'ok')
        # axs1.plot(opt_d_x, opt_d_y, 'b')
        # axs1.plot(opt_a_x, opt_a_y, 'r')

        #
        axs2.grid(b=True, which='major', color='black', linestyle='-')
        acs = axs2.contourf(X, Y, np_attacker_data, cmap=camap)
        fig.colorbar(acs, ax=axs2)
        # axs2.plot(data_x, data_y, 'ok')
        # axs2.plot(opt_d_x, opt_d_y, 'b')
        # axs2.plot(opt_a_x, opt_a_y, 'r')


    def show_plot(self):

        self.__plot()
        plt.show()

    def save_plot(self, location, name):

        self.__plot()
        plt.savefig(location + '/' + name, bbox_inches='tight')


    def calculate_periodic_equilibrium(self):

        defender_costs = self.defender.get_player_properties()['move_costs'][0]
        attacker_costs = self.attacker.get_player_properties()['move_costs'][0]

        if defender_costs < attacker_costs:
            return 1 / (2 * attacker_costs), defender_costs / (2 * attacker_costs ** 2)
        elif defender_costs == attacker_costs:
            return 1 / (2 * defender_costs), 1 / (2 * defender_costs)
        else:
            return attacker_costs / (2 * defender_costs ** 2), 1 / (2 * defender_costs)

    def periodic_opt_response(self, player, opponent):
        move_cost = player.get_player_properties()['move_costs'][0]
        test = 1 / (2 * move_cost)
        opponent_rate = opponent.get_player_properties()['rates'][0]
        if opponent_rate < test:
            return math.sqrt(opponent_rate * test)
        else:
            return 0



# base_defender_properties['delay'] = 1.0
#
# defender = Periodic("Defender 1", copy(base_defender_properties))
# attacker = LastMovePeriodic("Attacker 1", copy(base_attacker_properties))
#
# it = Iterate(defender, attacker, [0.01, 0.6], [0.01, 0.6])
# it.start_iteration(0.05)
#
# it.show_plot()
#

costs = [(1.0, 3.0)]



for cost in costs:
    base_defender_properties['move_costs'] = (cost[0], )
    base_attacker_properties['move_costs'] = (cost[1], )

    defender = Player("Defender ", strategies=(Periodic(1.0),))
    attacker = Player("Attacker ", strategies=(Periodic(1.0),))

    it = Iterate(defender, attacker, [0.01, 0.6], [0.01, 0.6])
    it.start_iteration(0.1)
    name = "d" + str(int(cost[0])) + "a" + str(int(cost[1]))
    it.save_plot("../../PhD/MyWork/Updates/Main/Images/Software/FlipIt/", name)

