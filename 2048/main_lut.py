import numpy as np
import time
import random
from generate_lookup_table import generate_move_tables, generate_possible_tables

def array_to_state(grid):
    state = 0
    for r in range(4):
        for c in range(4):
            val = grid[r][c]
            state |= (int(val) & 0xF) << ((r * 16) + ((3 - c) * 4))
    return state


def print_state(state):
    for row in range(4):
        shift = row * 16
        line = [str((state >> (shift + (3 - col) * 4)) & 0xF) for col in range(4)]
        print(' '.join(line))

def transpose(state):
    r0 = state & 0xFFFF
    r1 = (state >> 16) & 0xFFFF
    r2 = (state >> 32) & 0xFFFF
    r3 = (state >> 48) & 0xFFFF
    
    return (
        ((r0 >> 12) & 0xF) << 12 | ((r0 >> 8) & 0xF) << 28 | ((r0 >> 4) & 0xF) << 44 | (r0 & 0xF) << 60 |
        ((r1 >> 12) & 0xF) << 8  | ((r1 >> 8) & 0xF) << 24 | ((r1 >> 4) & 0xF) << 40 | (r1 & 0xF) << 56 |
        ((r2 >> 12) & 0xF) << 4  | ((r2 >> 8) & 0xF) << 20 | ((r2 >> 4) & 0xF) << 36 | (r2 & 0xF) << 52 |
        ((r3 >> 12) & 0xF)       | ((r3 >> 8) & 0xF) << 16 | ((r3 >> 4) & 0xF) << 32 | (r3 & 0xF) << 48
    )

def add_random_tile(state):
    empty_indices = []
    for shift in range(0, 64, 4):
        if (state >> shift) & 0xF == 0:
            empty_indices.append(shift)
            
    if not empty_indices:
        return state
        
    target_shift = random.choice(empty_indices)
    tile_value = 1 if random.random() < 0.9 else 2
    return state | (tile_value << target_shift)

def move_state(state, moves_left, moves_right, direction):
    if direction == 'r':
        row0 = moves_right[state & 0xFFFF]
        row1 = moves_right[(state >> 16) & 0xFFFF]
        row2 = moves_right[(state >> 32) & 0xFFFF]
        row3 = moves_right[(state >> 48) & 0xFFFF]
        return row0 | (row1 << 16) | (row2 << 32) | (row3 << 48)
    elif direction == 'l':
        row0 = moves_left[state & 0xFFFF]
        row1 = moves_left[(state >> 16) & 0xFFFF]
        row2 = moves_left[(state >> 32) & 0xFFFF]
        row3 = moves_left[(state >> 48) & 0xFFFF]
        return row0 | (row1 << 16) | (row2 << 32) | (row3 << 48)
    elif direction == 'u':
        state_t = transpose(state)
        # For upward moves we must collapse the transposed rows to the left
        row0 = moves_left[state_t & 0xFFFF]
        row1 = moves_left[(state_t >> 16) & 0xFFFF]
        row2 = moves_left[(state_t >> 32) & 0xFFFF]
        row3 = moves_left[(state_t >> 48) & 0xFFFF]
        return transpose(row0 | (row1 << 16) | (row2 << 32) | (row3 << 48))
    elif direction == 'd':
        state_t = transpose(state)
        # For downward moves collapse transposed rows to the right.
        row0 = moves_right[state_t & 0xFFFF]
        row1 = moves_right[(state_t >> 16) & 0xFFFF]
        row2 = moves_right[(state_t >> 32) & 0xFFFF]
        row3 = moves_right[(state_t >> 48) & 0xFFFF]
        return transpose(row0 | (row1 << 16) | (row2 << 32) | (row3 << 48))

def check_valid(state, can_left, can_right):
    valid = []
    # Check right
    for i in range(4):
        row = (state >> (i * 16)) & 0xFFFF
        if can_right[row]:
            valid.append('r')
            break
    for i in range(4):
        row = (state >> (i * 16)) & 0xFFFF
        if can_left[row]:
            valid.append('l')
            break
    state_t = transpose(state)
    for i in range(4):
        row = (state_t >> (i * 16)) & 0xFFFF
        # can_right on the transposed row means an upward move is possible
        if can_right[row]:
            valid.append('u')
            break
    for i in range(4):
        row = (state_t >> (i * 16)) & 0xFFFF
        # can_left on the transposed row means a downward move is possible
        if can_left[row]:
            valid.append('d')
            break
    return valid

def play_random_game(move_left, move_right, can_left, can_right):
    state = add_random_tile(0)
    i = 0
    while True:
        moves = check_valid(state, can_left, can_right)
        if not moves:
            return i
        choice = random.choice(moves)
        state = move_state(state, move_left, move_right, choice)
        state = add_random_tile(state)
        i += 1

if __name__ == "__main__":
    _move_left, _move_right = generate_move_tables()
    _can_left, _can_right = generate_possible_tables(_move_left, _move_right)
    
    move_left = _move_left.tolist()
    move_right = _move_right.tolist()
    can_left = _can_left.tolist()
    can_right = _can_right.tolist()

    # state = add_random_tile(0)
    # while True:
    #     print_state(state)
    #     moves = check_valid(state,can_left, can_right)
    #     if not moves:
    #         print('No valid moves remaining. Game over.')
    #         break
    #     choice = input(f'Choose one of the following directions: {moves} -->')
    #     if(choice not in moves):
    #         print(f'Invalid direction, quitting...')
    #         exit()
    #     state = move_state(state, move_left, move_right, choice)
    #     state = add_random_tile(state)
    # timing: run 1000 random games and report total + average time
    runs = 100
    t0 = time.perf_counter()
    for i in range(runs):
        _ = play_random_game(move_left, move_right, can_left, can_right)
    t1 = time.perf_counter()
    total = t1 - t0
    print(f"main_lut: ran {runs} games in {total:.4f}s, avg {total / runs:.6f}s/game")
        