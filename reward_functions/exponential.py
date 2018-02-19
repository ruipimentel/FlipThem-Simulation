import itertools
import tools
import numpy as np

import reward_functions.renewal
import matplotlib.pyplot as plt


def reward(threshold, defender_rates, attacker_rates, defender_costs, attacker_costs):
    n = len(defender_rates)
    if n != (len(attacker_rates) and len(defender_costs) and len(attacker_costs)):
        raise Exception("Unequal set of lists")
    else:
        resources = list(range(0, n))
        subsets = []
        for t in range(threshold, n + 1):
            subsets.append(list(itertools.combinations(resources, t)))

        subsets = tools.flatten(subsets)

        if () in subsets and len(defender_costs) != 1:
            subsets.remove(())

        gain = 0
        for l in subsets:
            # creating the product
            p = 1
            for i in range(0, n):
                p *= 1/(defender_rates[i] + attacker_rates[i])

                if i in l:
                    p *= attacker_rates[i]
                else:
                    p *= defender_rates[i]
            gain += p

        defender_move_cost = 0
        attacker_move_cost = 0
        for i in range(0, n):
            defender_move_cost += defender_rates[i] * defender_costs[i]
            attacker_move_cost += attacker_rates[i] * attacker_costs[i]

        defender_reward = 1 - gain - defender_move_cost
        attacker_reward = gain - attacker_move_cost

        return defender_reward, attacker_reward

def equilibrium(threshold, defender_costs, attacker_costs):

    # Iterate through each
    n = len(defender_costs)
    if n != len(attacker_costs):
        raise Exception("Unequal set of lists")
    else:
        def_equilibrium = []
        att_equilibrium = []

        for i in range(0, n):
            # print("Resource: ", i)
            # print("----------------")
            resources = list(range(0, n))
            resources.remove(i)
            #
            # print("Resources: ", resources)

            subsets = []
            # for t in range(threshold-1, n):
            subsets.append(list(itertools.combinations(resources, threshold-1)))

            # print("Before flatten: ", subsets)
            subsets = tools.flatten(subsets)
            # print("Subsets:", subsets)
            # subsets.append([])
            if () in subsets and len(defender_costs) != 1:
                subsets.remove(())
            # print("Subsets: ", subsets)
            s = 0
            for l in subsets:
                # creating the product
                p = 1
                for j in range(0, n):
                    if j == i:
                        continue
                    if j in l:
                        p *= defender_costs[j]/(defender_costs[j] + attacker_costs[j])
                    else:
                        p *= attacker_costs[j]/(defender_costs[j] + attacker_costs[j])

                s += p

            s /= ((attacker_costs[i] + defender_costs[i])**2)
            defender_point = s * attacker_costs[i]
            attacker_point = s * defender_costs[i]

            def_equilibrium.append(defender_point)
            att_equilibrium.append(attacker_point)

        return def_equilibrium, att_equilibrium


def age_density(z, rate):

    return rate * np.exp(-rate * z)

def age_distribution(z, rate):
    return 1 - np.exp(-rate * z)



if __name__ == '__main__':

    def_cost = (0.2,)
    att_cost = (0.2,)
    threshold = 1

    print(equilibrium(threshold, def_cost, att_cost))


    if True:
        print(
            reward_functions.renewal.reward(threshold, ((age_density,), (age_distribution,)), ((age_density,), (age_distribution,)),
                                            (0.7,), (1.0,), def_cost, att_cost))

        print(
            reward_functions.renewal.reward(1, ((age_density,), (age_distribution,)), ((age_density,), (age_distribution,)),
                                            (0.01,), (1.0,), def_cost, att_cost))


    if True:
        y1 = []
        y2 = []
        x = np.arange(0.01, 3, 0.01)
        for i in x:

            y1.append(reward_functions.renewal.reward(1, ((age_density,), (age_distribution,)), ((age_density,), (age_distribution,)),
                                            (i,), (1.25,), def_cost, att_cost)[0])

            y2.append(reward_functions.renewal.reward(1, ((age_density,), (age_distribution,)),
                                                      ((age_density,), (age_distribution,)),
                                                      (i,), (0.8,), def_cost, att_cost)[1])


        plt.plot(y1)
        plt.plot(y2)

        plt.show()
