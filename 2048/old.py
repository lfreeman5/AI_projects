import numpy as np
import time



def add_tile(state):
    # efficient way: search state for 
    # 10% chance to spawn a 10
    rows, cols = np.where(state==0)
    if(rows.size>0):
        i = np.random.randint(0,rows.size)
        state[rows[i], cols[i]] = 2 if np.random.rand()<0.9 else 4
        return state
    else: # board is full, game over
        return None
    
def which_moves_viable(state):
    viable = []
    if any(can_move_column_right(state[i]) for i in range(4)):
        viable.append('r')
    if any(can_move_column_right(np.flip(state[i])) for i in range(4)):
        viable.append('l')
    if any(can_move_column_right(np.flip(state[:, j])) for j in range(4)):
        viable.append('u')
    if any(can_move_column_right(state[:, j]) for j in range(4)):
        viable.append('d')
    return viable

def can_move_column_right(vec):
    if(np.any(vec[1:]==0)):
        return True
    if(vec[0]==vec[1]):
        return True
    if(vec[1]==vec[2]):
        return True
    if(vec[2]==vec[3]):
        return True
    return False


def collapse(state, direction):
    code=1 # successful
    if(direction=='r'):
        for i in range(4):
            state[i] = collapse_right(state[i])
    elif(direction=='l'):
        for i in range(4):
            state[i] = np.flip(collapse_right(np.flip(state[i])))
    elif(direction=='u'):
        for j in range(4):
            state[:,j] = np.flip(collapse_right(np.flip(state[:,j])))
    elif(direction=='d'):
        for j in range(4):
            state[:,j] = collapse_right(state[:,j])
    return state

def collapse_right(vec):
    for j in range(1,4):
        if(vec[j]==0): # move to right hand side getting rid of zeros
            vec[1:j+1] = vec[:j]
            vec[0] = 0
    for j in range(3,0,-1): # match numbers
        if(vec[j]==vec[j-1]):
            vec[j]*=2
            vec[1:j] = vec[0:j-1]
            vec[0] = 0
    return vec


def print_matrix(matrix):
    rows = [list(map(str, row)) for row in matrix]
    width = max(len(item) for row in rows for item in row)
    print()
    for row in rows:
        print(" ".join(item.rjust(width) for item in row))
    print()

def play_random_game():
    state = np.zeros((4,4), dtype=np.int32)
    state = add_tile(state)
    i = 0
    while True:
        valid_moves = which_moves_viable(state)
        if not valid_moves:
            return i
        dir = np.random.choice(valid_moves)
        state = collapse(state,dir)
        i+=1
        state = add_tile(state)
        if(state is None):
            return i

if __name__ == "__main__":
    runs = 100
    t0 = time.perf_counter()
    for i in range(runs):
        _ = play_random_game()
    t1 = time.perf_counter()
    total = t1 - t0
    print(f"old: ran {runs} games in {total:.4f}s, avg {total / runs:.6f}s/game")


### NEXT SWAP TO LOOKUP TABLE