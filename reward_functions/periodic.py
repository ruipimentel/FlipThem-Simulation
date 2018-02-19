import math
import reward_functions.renewal
import matplotlib.pyplot as plt
import numpy as np

def calculate_periodic_equilibrium(defender_costs, attacker_costs):

    if defender_costs[0] < attacker_costs[0]:
        return 1 / (2 * attacker_costs[0]), defender_costs[0] / (2 * attacker_costs[0] ** 2)
    elif defender_costs[0] == attacker_costs[0]:
        return 1 / (2 * defender_costs[0]), 1 / (2 * defender_costs[0])
    else:
        return attacker_costs[0] / (2 * defender_costs[0] ** 2), 1 / (2 * defender_costs[0])


def periodic_opt_response(player, opponent):
    move_cost = player.get_player_properties()['move_costs'][0]
    test = 1 / (2 * move_cost)
    opponent_rate = opponent.get_player_properties()['rates'][0]
    if opponent_rate < test:
        return math.sqrt(opponent_rate * test)
    else:
        return 0


def age_density(z, rate):
    if z < 1 / rate:
        return rate
    else:
        return 0


def age_distribution(z, rate):
    if z < 1 / rate:
        return rate * z
    else:
        return 1


if __name__ == '__main__':


    print(calculate_periodic_equilibrium((0.4,), (0.3,)))

    if False:

        print(
            reward_functions.renewal.reward(1, ((age_density,), (age_distribution,)), ((age_density,), (age_distribution,)),
                                            (0.001,), (2.5,), (0.2,), (0.2,)))
        print(
            reward_functions.renewal.reward(1, ((age_density,), (age_distribution,)), ((age_density,), (age_distribution,)),
                                            (0.142,), (2.5,), (0.2,), (0.2,)))

    if True:
        y1 = []
        y2 = []
        x = np.arange(0.01, 3, 0.01)
        for i in x:

            temp = reward_functions.renewal.reward(1, ((age_density,), (age_distribution,)), ((age_density,), (age_distribution,)),
                                                  (i,), (2.5,), (0.2,), (0.2,))

            y1.append(temp[0])

            y2.append(temp[1])



        d, = plt.plot(x, y1, label='Defender',c='blue')
        a, = plt.plot(x, y2,label='Attacker', c='red')

        plt.xlabel('Defender rate')
        plt.ylabel('Payoff')

        plt.legend(handles=[d, a])

        plt.show()
