from system import System
from old_tournament import Tournament
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.periodic import Periodic
from strategies.player import Player

from copy import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from itertools import product



example_tournament_properties = {
    'number_of_rounds': 50,
    'attacker_threshold': 1,
    'defender_threshold': 1,
    'selection_ratio': 1.0
}

example_game_properties = {
    'time_limit': 1000.0
}


class MultiIterate:

    def __init__(self, number_of_resources, defender, attacker, defender_range, attacker_range):

        self.number_of_resources = number_of_resources
        self.defender = defender
        self.attacker = attacker
        self.defender_range = defender_range
        self.attacker_range = attacker_range
        self.defender_data = np.array([])
        self.attacker_data = np.array([])
        self.defender_steps = []
        self.attacker_steps = []

    def start_iteration(self, increment_size):


        # Need the steps to be a list of linspaces
        self.defender_steps = [np.linspace(r[0], r[1],
                                           (r[1] - r[0]) / increment_size) for r in self.defender_range]

        self.attacker_steps = [np.linspace(r[0], r[1],
                                           (r[1] - r[0]) / increment_size) for r in self.attacker_range]

        defender_data = []
        attacker_data = []

        round = 0

        for us in product(*self.defender_steps):

            self.defender.get_player_properties()['rates'] = us

            defender_list = []
            attacker_list = []

            for ls in product(*self.attacker_steps):
                self.attacker.get_player_properties()['rates'] = ls

                round += 1

                t = Tournament(defender_strategies=(defender,), attacker_strategies=(attacker,),
                               system=System(self.number_of_resources), game_properties=example_game_properties,
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

        np_defender_data = np.ma.masked_where(np_defender_data <= 0.0, np_defender_data)
        np_attacker_data = np.ma.masked_where(np_attacker_data <= 0.0, np_attacker_data)

        axs1.grid(b=True, which='major', color='black', linestyle='-')
        dcs = axs1.contourf(X, Y, np_defender_data, cmap=cdmap)
        fig.colorbar(dcs, ax=axs1, format="%.2f")

        axs2.grid(b=True, which='major', color='black', linestyle='-')
        acs = axs2.contourf(X, Y, np_attacker_data, cmap=camap)
        fig.colorbar(acs, ax=axs2)


    def show_plot(self):

        self.__plot()
        plt.show()

    def save_plot(self, location, name):

        self.__plot()
        plt.savefig(location + '/' + name, bbox_inches='tight')


base_attacker_properties = {
    'multi_rate': True,
    'rates': (0.01, 0.01),
    'keep_move_until_completed': True,
    'individual_move_costs': True,
    'move_costs': (1.0, 1.0, 1.0),
    'threshold': 3
}

base_defender_properties = {
    'multi_rate': True,
    'rates': (0.01, 0.01),
    'keep_move_until_completed': True,
    'individual_move_costs': True,
    'move_costs': (1.0, 1.0, 1.0),
    'threshold': 1
}

defender = Player("Defender ", strategies=Periodic(1.0))
attacker = Player("Attacker ", strategies=Periodic(1.3))

n = 1

it = MultiIterate(n, defender, attacker, [[0.01, 0.6]] * n, [[0.01, 0.6]] * n)
it.start_iteration(0.25)

it.show_plot()

