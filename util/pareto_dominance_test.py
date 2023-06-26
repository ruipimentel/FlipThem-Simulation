import pytest

import util.pareto_dominance as pd

def test_pareto_dominates():
    assert pd.pareto_dominates((0,), (0,)) == False
    assert pd.pareto_dominates((0,), (1,)) == False
    assert pd.pareto_dominates((1,), (0,)) == True
    assert pd.pareto_dominates((1,), (1,)) == False

    assert pd.pareto_dominates((0, 0), (0, 0)) == False
    assert pd.pareto_dominates((0, 0), (0, 1)) == False
    assert pd.pareto_dominates((0, 0), (1, 0)) == False
    assert pd.pareto_dominates((0, 0), (1, 1)) == False
    assert pd.pareto_dominates((0, 1), (0, 0)) == True
    assert pd.pareto_dominates((0, 1), (0, 1)) == False
    assert pd.pareto_dominates((0, 1), (1, 0)) == False
    assert pd.pareto_dominates((0, 1), (1, 1)) == False
    assert pd.pareto_dominates((1, 0), (0, 0)) == True
    assert pd.pareto_dominates((1, 0), (0, 1)) == False
    assert pd.pareto_dominates((1, 0), (1, 0)) == False
    assert pd.pareto_dominates((1, 0), (1, 1)) == False
    assert pd.pareto_dominates((1, 1), (0, 0)) == True
    assert pd.pareto_dominates((1, 1), (0, 1)) == True
    assert pd.pareto_dominates((1, 1), (1, 0)) == True
    assert pd.pareto_dominates((1, 1), (1, 1)) == False

def test_non_pareto_dominated_insert():
    arr = []
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'a', 'value': (1, 1) }) == True
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'a', 'value': (1, 1) }) == False
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'b', 'value': (1, 0) }) == False
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'c', 'value': (0, 1) }) == False
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'd', 'value': (0, 0) }) == False
    assert len(arr) == 1    # a:(1, 1)
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'e', 'value': (1, 2) }) == True
    assert len(arr) == 1    # e:(1, 2)
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'f', 'value': (2, 1) }) == True
    assert len(arr) == 2    # e:(1, 2), f:(2, 1)
    assert pd.non_pareto_dominated_insert(arr, { 'point': 'g', 'value': (2, 2) }) == True
    assert len(arr) == 1    # g:(2, 2)
