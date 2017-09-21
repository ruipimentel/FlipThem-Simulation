import numpy as np
import matplotlib.pyplot as plt

class Plot(object):

    def __init__(self):
        self.plt = plt

    def plot(self, server, player, time_limit, colour='b'):
        pr1 = np.array([server.get_reward_for_player(player, i / 100.0) for i in range(0, time_limit*100, 1)])
        x = np.array([x / 100.0 for x in range(0, 1000, 1)])

        player1_reward = plt.plot(x, pr1)
        self.plt.setp(player1_reward, color=colour, linewidth=2.0)

    def show(self):
        self.plt.show()


