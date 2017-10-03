import itertools
import tools

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

        gain = 0
        for l in subsets:
            # creating the product
            p = 1
            for i in range(0,n):
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
            resources = list(range(0, n))
            resources.remove(i)

            subsets = []
            for t in range(threshold, n + 1):
                subsets.append(list(itertools.combinations(resources, t)))

            subsets = tools.flatten(subsets)
            subsets.append([])
            s = 0
            for l in subsets:
                # creating the product
                p = 1
                for j in range(0, n):
                    p *= 1 / (defender_costs[j] + attacker_costs[j])

                    if j == i:
                        pass
                    if j in l:
                        p *= defender_costs[i]
                    else:
                        p *= attacker_costs[i]

                s += p

            defender_point = s * (attacker_costs[i] / (attacker_costs[i] + defender_costs[i]))
            attacker_point = s * (defender_costs[i] / (attacker_costs[i] + defender_costs[i]))

            def_equilibrium.append(defender_point)
            att_equilibrium.append(attacker_point)

        print(def_equilibrium, att_equilibrium)

        return def_equilibrium, att_equilibrium

# #
# d_reward, a_reward = reward(2, [0.2 ,0.8],[0.5, 0.1], [0.3, 0.2], [0.4, 0.3])
# #
# # def_equilibrium, att_equilibrium = equilibrium(2, [0.3, 0.2, 0.3], [0.04, 0.03, 0.03])
#
# def_equilibrium, att_equilibrium = equilibrium(1, [0.3], [0.04])


# def_equilibrium, att_equilibrium = equilibrium(2, [0.3, 0.3], [0.04, 0.03])
# print(d_reward, a_reward)
#
# print('---------')
# print(def_equilibrium, att_equilibrium)