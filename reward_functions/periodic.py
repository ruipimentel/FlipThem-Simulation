
# TODO With i could generalise this
def calculate_periodic_equilibrium(defender_cost, attacker_cost):

        if defender_cost < attacker_cost:
            return 1 / (2 * attacker_cost), defender_cost / (2 * attacker_cost ** 2)
        elif defender_cost == attacker_cost:
            return 1 / (2 * defender_cost), 1 / (2 * defender_cost)
        else:
            return attacker_cost / (2 * defender_cost ** 2), 1 / (2 * defender_cost)