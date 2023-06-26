from typing import List

def pareto_dominates(solution_values_1, solution_values_2):
    """
    Returns `True` if `solution_values_1` dominates `solution_values_2` based on
    Pareto dominance. That is, the values from solution 1 must be always better or
    equal to the values from solution 2, and at least one of them are strictly better.

    Assumes maximization problems, that is, smaller values are considered worse.
    """
    dominates = False
    for i in range(len(solution_values_1)):
        if solution_values_1[i] < solution_values_2[i]:
            return False
        elif solution_values_1[i] > solution_values_2[i]:
            dominates = True
    return dominates

def non_pareto_dominated_insert(population: List, new_individual):
    """
    Inserts `new_individual` into `population` if and only if it is not dominated by
    any existing individual.

    Also disposes of any individual that is dominated by the new individual.

    Assumes that future insertions of a same `'point'` will have the same `'value'`.
    """
    for i, existing_individual in list(enumerate(population))[::-1]:
        if pareto_dominates(existing_individual['value'], new_individual['value']):
            return False
        elif existing_individual['point'] == new_individual['point']:
            return False
        elif pareto_dominates(new_individual['value'], existing_individual['value']):
            population.pop(i)
    population.append(new_individual)
    return True
