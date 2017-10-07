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


def full_threshold_equilibrium(n, defender_costs, attacker_costs):

    defender_equilibrium = []
    attacker_equilibrium = []

    for i in range(0, n):
        outer = 1/((attacker_costs[i] + defender_costs[i]))**2
        prod = 1
        for j in range(0, n):
            if j != i:
                prod *= (defender_costs[j]/(attacker_costs[j] + defender_costs[j]))

        total = outer * prod

        defender_equilibrium.append(attacker_costs[i] * total)
        attacker_equilibrium.append(defender_costs[i] * total)

    return defender_equilibrium, attacker_equilibrium



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
            for t in range(threshold-1, n):
                subsets.append(list(itertools.combinations(resources, t)))

            # print(subsets)
            subsets = tools.flatten(subsets)
            # print("Subsets:", subsets)
            # subsets.append([])
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


def t_defender_equilibrium(defender_cost, attacker_cost):
    return attacker_cost[0] / (defender_cost[0] + attacker_cost[0]) ** 2


def t_attacker_equilibrium(defender_cost, attacker_cost):
    return defender_cost[0] / (defender_cost[0] + attacker_cost[0]) ** 2


# #
#
# # #
# def_equilibrium, att_equilibrium = equilibrium(2, (0.02, 0.01), (0.03, 0.01))
# #
# d_reward, a_reward = reward(2, def_equilibrium, att_equilibrium, (0.02, 0.01), (0.03, 0.01))
#
# defender_costs = [0.2, ]
# attacker_costs =  [0.3, ]
#
# print("1 RESOURCE")
#
# print(equilibrium(1, defender_costs, attacker_costs))
# print("-----------")
# print(t_defender_equilibrium(defender_costs[0], attacker_costs[0]), t_attacker_equilibrium(defender_costs[0], attacker_costs[0]))
# print("-----------")
# print(full_threshold_equilibrium(1, defender_costs, attacker_costs))
# print("=======================")
#
#
# defender_costs = [0.2, 0.3]
# attacker_costs = [0.3, 0.1]
#
#
# print("2 RESOURCE")
#
# print(equilibrium(2, defender_costs, attacker_costs))
# print("-----------")
# print(full_threshold_equilibrium(2, defender_costs, attacker_costs))
# print("=======================")
#



