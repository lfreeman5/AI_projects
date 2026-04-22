import numpy as np
import time
import random

def collapse_right(vec):
    added_score = 0 # 
    for j in range(1,4):
        if(vec[j]==0): # move to right hand side getting rid of zeros
            vec[1:j+1] = vec[:j]
            vec[0] = 0
    for j in range(3,0,-1): # match numbers
        if(vec[j]==vec[j-1]):
            vec[j]+=1
            added_score += vec[j]
            vec[1:j] = vec[0:j-1]
            vec[0] = 0
    return vec, added_score


def print_state(state):
    print()
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


def add_random_tile_state(state):
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
        row0 = moves_left[state_t & 0xFFFF]
        row1 = moves_left[(state_t >> 16) & 0xFFFF]
        row2 = moves_left[(state_t >> 32) & 0xFFFF]
        row3 = moves_left[(state_t >> 48) & 0xFFFF]
        return transpose(row0 | (row1 << 16) | (row2 << 32) | (row3 << 48))
    elif direction == 'd':
        state_t = transpose(state)
        row0 = moves_right[state_t & 0xFFFF]
        row1 = moves_right[(state_t >> 16) & 0xFFFF]
        row2 = moves_right[(state_t >> 32) & 0xFFFF]
        row3 = moves_right[(state_t >> 48) & 0xFFFF]
        return transpose(row0 | (row1 << 16) | (row2 << 32) | (row3 << 48))


def check_valid(state, can_left, can_right):
    valid = []
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
        if can_right[row]:
            valid.append('u')
            break
    for i in range(4):
        row = (state_t >> (i * 16)) & 0xFFFF
        if can_left[row]:
            valid.append('d')
            break
    return valid


def play_random_game(move_left, move_right, can_left, can_right):
    state = add_random_tile_state(0)
    i = 0
    while True:
        moves = check_valid(state, can_left, can_right)
        if not moves:
            return i
        choice = random.choice(moves)
        state = move_state(state, move_left, move_right, choice)
        state = add_random_tile_state(state)
        print_state(state)
        i += 1