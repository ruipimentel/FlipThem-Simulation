import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

class Plot2(object):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.xdata, self.ydata = [], []
        self.plt = plt
        self.ln, = self.plt.plot([], [], animated=True)
        self.server = None
        self.player = None


    def plot(self, server, player, time_limit, colour='b'):
        self.server = server
        self.player = player
        # pr1 = np.array([server.get_reward_for_player(player, i / 100.0) for i in range(0, time_limit * 100, 1)])
        # self.xdata = np.array([x / 100.0 for x in range(0, 1000, 1)])

        # player1_reward = plt.plot(x, pr1)
        # self.plt.setp(player1_reward, color=colour, linewidth=2.0)

        ani = FuncAnimation(self.fig, self.update, frames=np.linspace(0, 10, 1000),
                            init_func=self.init, interval=25, blit=True)

        self.plt.show()

    def init(self):
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(-0.5, 10)
        return self.ln,

    def update(self, frame):
        self.xdata.append(frame)
        self.ydata.append(self.server.get_reward_for_player(self.player, frame))
        self.ln.set_data(self.xdata, self.ydata)

        return self.ln,

p = Plot2()
