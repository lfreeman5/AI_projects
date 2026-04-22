import time
from generate_lookup_table import generate_move_tables, generate_possible_tables
from utilities import add_random_tile_state, check_valid, move_state, print_state, play_random_game

if __name__ == "__main__":
    _move_left, _move_right, _added_left, _added_right = generate_move_tables()
    _can_left, _can_right = generate_possible_tables(_move_left, _move_right)
    
    move_left = _move_left.tolist()
    move_right = _move_right.tolist()
    can_left = _can_left.tolist()
    can_right = _can_right.tolist()
    added_left = _added_left.tolist()
    added_right = _added_right.tolist()

    play_random_game(move_left, move_right, can_left, can_right)
    exit()

    runs = 1000
    t0 = time.perf_counter()
    for i in range(runs):
        _ = play_random_game(move_left, move_right, can_left, can_right)
        if(i%100==0):
            print(_)
    t1 = time.perf_counter()
    total = t1 - t0
    print(f"main_lut: ran {runs} games in {total:.4f}s, avg {total / runs:.6f}s/game")
        