from sympy import symbols
import sympy
from reward_functions.exponential import full_threshold_equilibrium, equilibrium
from reward_functions.exponential import reward

d = [symbols('d1'), symbols('d2'), symbols('d3')]
a = [symbols('a1'), symbols('a2'), symbols('a3')]

l = [symbols('l1'), symbols('l2'), symbols('l3')]
u = [symbols('u1'), symbols('u2'), symbols('u3')]

defender_ga_properties = {
    'name': "Defender ",
    'number_of_players': 50,

    'move_costs': (0.1, 0.1),
}

attacker_ga_properties = {
    'name': "Attacker ",
    'number_of_players': 50,
    'move_costs': (0.2, 0.21),
}




# print(full_threshold_equilibrium(3,d, a))
defe = equilibrium(3, d, a)[0][0]

# rew = reward(2, u, l, d, a)
# print(sympy.simplify(rew[0]), '\n\n\n\n\n\n\n')
print(sympy.simplify(defe))


# print(sympy.diff(rew, l[0]))
