import math

def reward(threshold, defender_rates, attacker_rates, defender_costs, attacker_costs):
    # For now assuming just one resource
    if threshold == 1:
        if defender_rates[0] >= attacker_rates[0]:
            gain = attacker_rates[0]/(2 * defender_rates[0])

            return 1 - gain - defender_costs[0] * defender_rates[0], gain - attacker_costs[0] * attacker_rates[0]
        else:
            gain = defender_rates[0] / (2 * attacker_rates[0])

            return gain - defender_costs * defender_rates[0], 1 - gain - attacker_costs[0] * attacker_rates[0]

    else:
        raise NotImplementedError("We don't have the formula yet")


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