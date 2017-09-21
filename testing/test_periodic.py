import strategies.non_adaptive.periodic as periodic
import system

base_properties = {
        'threshold': False,
        'time_limit': 100
    }

s = system.System(3)

player1 = periodic.Periodic("player 1")

initial_moves = player1.check_for_move_times(base_properties, s, 0)

print(initial_moves)

later_moves = player1.check_for_move_times(base_properties, s, 1.02)

print(later_moves)


player_properties = {
    'multi_rate': True,
    'rates': (1.2, 2.9, 0.7, 1.6),
    'default_rate': 1.0
}


player2 = periodic.Periodic("player 2", player_properties)



initial_moves2 = player2.check_for_move_times(base_properties, s, 0)

print(initial_moves2)

later_moves2 = player2.check_for_move_times(base_properties, s, 1.02)

print(later_moves2)