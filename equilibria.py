
# For full threshold exponential FlipThem


def def_equilibrium(server, defender_costs, attacker_costs):
    product = attacker_costs[server] / ((attacker_costs[server] + defender_costs[server]) ** 2)
    for i in range(0, len(defender_costs)):
        if i != server:
            product *= (defender_costs[i] / (attacker_costs[i] + defender_costs[i]))

    return product


def att_equilibrium(server, defender_costs, attacker_costs):

    temp = def_equilibrium(server, defender_costs, attacker_costs) * defender_costs[server]
    temp /= attacker_costs[server]

    return temp


def def_benefit(def_rates, def_costs, att_rates):
    product = 1
    costs = 0

    for i in range(0, len(def_costs)):
        product *= att_rates[i] / (att_rates[i] + def_rates[i])
        costs += def_costs[i] * def_rates[i]

    return 1 - product - costs


def att_benefit(def_rates, att_rates, att_costs):
    product = 1
    costs = 0

    for i in range(0, len(att_costs)):
        product *= att_rates[i] / (att_rates[i] + def_rates[i])
        costs += att_costs[i] * att_rates[i]

    return product - costs

#
# d = (0.08, 0.3, 0.9)
# a = (0.09, 0.04, 0.01)

# One resource

d = (1.0,)
a = (0.7,)

def_equ = []
att_equ = []

print("------ Defender ------")
for i in range(0, len(d)):
    def_equ.append(def_equilibrium(i, d, a))
    print("Resource:", i, def_equilibrium(i, d, a))

print("------ Attacker ------")
for i in range(0, len(a)):
    att_equ.append(att_equilibrium(i, d, a))
    print("Resource:", i, att_equilibrium(i, d, a))

print("----------")

print("Defender Benefit: ", def_benefit(def_equ, d, att_equ))
print("Attacker Benefit: ", att_benefit(def_equ, att_equ, a))
