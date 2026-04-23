import time
import random

def collapse_right(vec):
    added_score = 0 # 
    for j in range(1,4):
        if(vec[j]==0): # move to right hand side getting rid of zeros
            vec[1:j+1] = vec[:j]
            vec[0] = 0
    for j in range(3,0,-1): # match numbers
        if(vec[j]!=0 and vec[j]==vec[j-1]):
            vec[j]+=1
            added_score += vec[j]
            vec[1:j] = vec[0:j-1]
            vec[0] = 0
    return vec, added_score


def print_state(state):
    for row in range(4):
        shift = row * 16
        line = [str((state >> (shift + (3 - col) * 4)) & 0xF) for col in range(4)]
        print(' '.join(line))
    print()


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


def max_tile(state):
    max_value = 0
    for shift in range(0, 64, 4):
        tile = (state >> shift) & 0xF
        if tile > max_value:
            max_value = tile
            if max_value == 0xF:
                break
    return max_value


def split_state(state):
    return [
        (state >> (row * 16 + (3 - col) * 4)) & 0xF
        for row in range(4)
        for col in range(4)
    ]


def combine_state(tiles):
    state = 0
    for idx, tile in enumerate(tiles):
        row = idx // 4
        col = idx % 4
        state |= (int(tile) & 0xF) << (row * 16 + (3 - col) * 4)
    return state


def add_random_tile_state(state):
    state = int(state)
    empty_indices = []
    for shift in range(0, 64, 4):
        if (state >> shift) & 0xF == 0:
            empty_indices.append(shift)
            
    if not empty_indices:
        return state
        
    target_shift = int(random.choice(empty_indices))
    tile_value = 1 if random.random() < 0.9 else 2
    return state | (tile_value << target_shift)


def move_state(state, lut, direction):
    moves_left = lut['move_left']
    moves_right = lut['move_right']
    added_left = lut['added_left']
    added_right = lut['added_right']

    if direction == 1:  # r
        added = 0
        row0 = int(moves_right[state & 0xFFFF])
        added += added_right[state & 0xFFFF]
        row1 = int(moves_right[(state >> 16) & 0xFFFF])
        added += added_right[(state >> 16) & 0xFFFF]
        row2 = int(moves_right[(state >> 32) & 0xFFFF])
        added += added_right[(state >> 32) & 0xFFFF]
        row3 = int(moves_right[(state >> 48) & 0xFFFF])
        added += added_right[(state >> 48) & 0xFFFF]
        return row0 | (row1 << 16) | (row2 << 32) | (row3 << 48), added
    elif direction == 0:  # l
        added = 0
        row0 = int(moves_left[state & 0xFFFF])
        added += added_left[state & 0xFFFF]
        row1 = int(moves_left[(state >> 16) & 0xFFFF])
        added += added_left[(state >> 16) & 0xFFFF]
        row2 = int(moves_left[(state >> 32) & 0xFFFF])
        added += added_left[(state >> 32) & 0xFFFF]
        row3 = int(moves_left[(state >> 48) & 0xFFFF])
        added += added_left[(state >> 48) & 0xFFFF]
        return row0 | (row1 << 16) | (row2 << 32) | (row3 << 48), added
    elif direction == 2:  # u
        added = 0
        state_t = transpose(state)
        row0 = int(moves_left[state_t & 0xFFFF])
        added += added_left[state_t & 0xFFFF]
        row1 = int(moves_left[(state_t >> 16) & 0xFFFF])
        added += added_left[(state_t >> 16) & 0xFFFF]
        row2 = int(moves_left[(state_t >> 32) & 0xFFFF])
        added += added_left[(state_t >> 32) & 0xFFFF]
        row3 = int(moves_left[(state_t >> 48) & 0xFFFF])
        added += added_left[(state_t >> 48) & 0xFFFF]
        return transpose(row0 | (row1 << 16) | (row2 << 32) | (row3 << 48)), added
    elif direction == 3:  # d
        added = 0
        state_t = transpose(state)
        row0 = int(moves_right[state_t & 0xFFFF])
        added += added_right[state_t & 0xFFFF]
        row1 = int(moves_right[(state_t >> 16) & 0xFFFF])
        added += added_right[(state_t >> 16) & 0xFFFF]
        row2 = int(moves_right[(state_t >> 32) & 0xFFFF])
        added += added_right[(state_t >> 32) & 0xFFFF]
        row3 = int(moves_right[(state_t >> 48) & 0xFFFF])
        added += added_right[(state_t >> 48) & 0xFFFF]
        return transpose(row0 | (row1 << 16) | (row2 << 32) | (row3 << 48)), added
    else:
        print("Invalid move direction, how did you do that?")
        exit()

def take_step(state, action, lut):
    # state is in 16-size format
    state = combine_state(state)
    # check if action is valid, if not return state and -1 reward
    valid = check_valid(state, lut['can_left'], lut['can_right'])
    if not valid: # game over!
        print("Game over, but shouldn't reach this point")
        exit()
        return split_state(state), 0, True
    if(action not in valid):
        return split_state(state), -1, False
    else:
        new_state, added_score = move_state(state, lut, action)
        new_state = add_random_tile_state(new_state)
        reward = max_tile(new_state) + added_score
        next_valid = check_valid(new_state, lut['can_left'], lut['can_right'])
        if not next_valid:
            return split_state(new_state), 0, True
        else:
            return split_state(new_state), reward, False

def check_valid(state, can_left, can_right):
    valid = []
    for i in range(4):
        row = (state >> (i * 16)) & 0xFFFF
        if can_right[row]:
            valid.append(1)
            break
    for i in range(4):
        row = (state >> (i * 16)) & 0xFFFF
        if can_left[row]:
            valid.append(0)
            break
    state_t = transpose(state)
    for i in range(4):
        row = (state_t >> (i * 16)) & 0xFFFF
        if can_right[row]:
            valid.append(2)
            break
    for i in range(4):
        row = (state_t >> (i * 16)) & 0xFFFF
        if can_left[row]:
            valid.append(3)
            break
    return valid


def play_random_game(lut):
    move_names = ["left", "right", "up", "down"]
    state = add_random_tile_state(0)
    i = 0
    while True:
        moves = check_valid(state, lut['can_left'], lut['can_right'])
        if not moves:
            return i
        choice = random.choice(moves)
        state, _ = move_state(state, lut, choice)
        state = add_random_tile_state(state)
        print("Moved board " + move_names[choice])
        print_state(state)
        i += 1