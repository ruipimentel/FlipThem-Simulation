from typing import Iterable

from strategies.server_strategies.server_strategy import ServerStrategy
from strategies.server_strategies.periodic import Periodic
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.lm_periodic import LastMove

def strategy_classes_to_str(strategy_classes: Iterable[ServerStrategy]):
    set_classes = set([ el.__name__ for el in strategy_classes ])
    print(set_classes)
    return '-'.join([code for code, cls_name in [
        ('P', Periodic.__name__),
        ('E', Exponential.__name__),
        ('LM', LastMove.__name__),
    ] if cls_name in set_classes])
