from sympy import symbols
import sympy
from reward_functions.exponential import full_threshold_equilibrium, equilibrium

d = [symbols('d1'), symbols('d2'), symbols('d3')]
a = [symbols('a1'), symbols('a2'), symbols('a3')]


# print(full_threshold_equilibrium(3,d, a))
defe = equilibrium(2, d, a)[0][0]


print(defe)
print(sympy.simplify(defe))
