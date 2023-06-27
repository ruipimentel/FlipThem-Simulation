import pytest

from util.classes import *

from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.lm_periodic import LastMove

def test_strategy_classes_to_str():
    assert strategy_classes_to_str([]) == ''
    assert strategy_classes_to_str(()) == ''
    assert strategy_classes_to_str([Periodic,]) == 'P'
    assert strategy_classes_to_str((Periodic,)) == 'P'
    assert strategy_classes_to_str([Exponential,]) == 'E'
    assert strategy_classes_to_str((Exponential,)) == 'E'
    assert strategy_classes_to_str([LastMove,]) == 'LM'
    assert strategy_classes_to_str((LastMove,)) == 'LM'
    assert strategy_classes_to_str([Periodic, Exponential]) == 'P-E'
    assert strategy_classes_to_str((Periodic, Exponential)) == 'P-E'
    assert strategy_classes_to_str([Exponential, Exponential]) == 'E'
    assert strategy_classes_to_str((Exponential, Exponential)) == 'E'
    assert strategy_classes_to_str([LastMove, Exponential]) == 'E-LM'
    assert strategy_classes_to_str((LastMove, Exponential)) == 'E-LM'
    assert strategy_classes_to_str([Periodic, Exponential, LastMove]) == 'P-E-LM'
    assert strategy_classes_to_str((Periodic, Exponential, LastMove)) == 'P-E-LM'
    assert strategy_classes_to_str([Exponential, LastMove, Exponential]) == 'E-LM'
    assert strategy_classes_to_str((Exponential, LastMove, Exponential)) == 'E-LM'
    assert strategy_classes_to_str([Periodic, LastMove, Exponential]) == 'P-E-LM'
    assert strategy_classes_to_str((Periodic, LastMove, Exponential)) == 'P-E-LM'
