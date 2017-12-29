from scipy import integrate
import numpy as np
import itertools
import tools


import reward_functions.exponential as exponential

def gain_func(z, def_function, att_function, def_rate, att_rate):
    return def_function(z, def_rate) * att_function(z, att_rate)


def reward(threshold=None, defender_functions=None, attacker_functions=None,
           defender_rates=None, attacker_rates=None, defender_costs=None, attacker_costs=None):

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

        # Iterate through all subsets with high enough threshold and sum the resulting gain
        gain = 0
        for subset in subsets:
            # Setting the product to 1
            # Iterate through the resource list and test whether it is in the current subset or not
            p = 1
            for resource in range(0, n):

                if resource in subset:
                    p *= integrate.quad(gain_func, 0, np.inf,
                                        args=(defender_functions[0][resource], attacker_functions[1][resource],
                                              defender_rates[resource], attacker_rates[resource]))[0]
                else:
                    p *= integrate.quad(gain_func, 0, np.inf,
                                        args=(defender_functions[1][resource], attacker_functions[0][resource],
                                              defender_rates[resource], attacker_rates[resource]))[0]

            gain += p

        defender_move_cost = 0
        attacker_move_cost = 0
        for resource in range(0, n):
            defender_move_cost += defender_rates[resource] * defender_costs[resource]
            attacker_move_cost += attacker_rates[resource] * attacker_costs[resource]

        defender_reward = 1 - gain - defender_move_cost
        attacker_reward = gain - attacker_move_cost

        return defender_reward, attacker_reward

#
# def ndm(*args):
#     return [x[(None,)*i+(slice(None),)+(None,)*(len(args)-i-1)] for i, x in enumerate(args)]


if __name__ == '__main__':
    n = 1
    t = 1

    defender_costs = (1,)
    attacker_costs = (2,)

    defender_rates = (0.5,)
    attacker_rates = (0.2,)

    #
    # defender_rates = np.linspace(0.01, 3.0, 100)
    # attacker_rates = np.linspace(0.01, 3.0, 100)

    defender_functions = ((exponential.age_density,), (exponential.age_distribution,))

    attacker_functions = ((exponential.age_density,), (exponential.age_distribution,))

    print(reward(t, defender_functions, attacker_functions, defender_rates,
                 attacker_rates, defender_costs, attacker_costs))

    # print(exponential.reward(t, defender_rates, attacker_rates, defender_costs, attacker_costs))