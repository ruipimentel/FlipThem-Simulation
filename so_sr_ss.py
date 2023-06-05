import argparse
parser = argparse.ArgumentParser(description='Parameterized single-objective, single-resource, single-strategy simulation')
parser.add_argument('-dmc', type=float, help='Defender move cost')
parser.add_argument('-amc', type=float, help='Attacker move cost')
parser.add_argument('-dr',  type=float, help='Defender base rate')
parser.add_argument('-ar',  type=float, help='Attacker base rate')
parser.add_argument('-dsc', type=str,   help='Defender strategy class')
parser.add_argument('-asc', type=str,   help='Attacker strategy class')
parser.add_argument('-tl',  type=float, help='Time limit for the simulation')
args = parser.parse_args()

from core.system import System
from strategies.player import Player
from strategies.server_strategies.exponential import Exponential
from strategies.server_strategies.lm_periodic import LastMove
from strategies.server_strategies.periodic import Periodic
from core.game import Game
from copy import copy

def generate_strategy(sc, r):
    if sc == 'P':
        return Periodic(r)
    elif sc == 'E':
        return Exponential(r)
    elif sc == 'L':
        return LastMove(r)
    else:
        raise f'Strategy "{sc}" not implemented!'

if __name__ == '__main__':
    s = System(1)

    # If threshold is 1, any player must control whole system for benefit:
    defender_properties = {
        'move_costs': (
            args.dmc,
        ),
        'threshold': 1,
    }
    attacker_properties = {
        'move_costs': (
            args.amc,
        ),
        'threshold': 1,
    }

    defender = Player(
        "Defender ",
        player_properties=copy(defender_properties),
        strategies=(
            generate_strategy(args.dsc, args.dr),
        ),
    )
    attacker = Player(
        "Attacker ",
        player_properties=copy(attacker_properties),
        strategies=(
            generate_strategy(args.asc, args.ar),
        ),
    )

    game_properties = {
        'time_limit': args.tl,
    }

    g = Game(players=(
        defender,
        attacker,
    ), system=s, game_properties=game_properties)
    g.play()
