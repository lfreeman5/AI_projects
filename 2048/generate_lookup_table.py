import numpy as np
from main import collapse_right

def extract_nibbles(x):
    # x between 0 and 65536, returns 4 bits
    x &= 0xFFFF
    return [
        (x >> 12) & 0xF,  # highest 4 bits
        (x >> 8)  & 0xF,
        (x >> 4)  & 0xF,
        x & 0xF           # lowest 4 bits
    ]

def pack_nibbles(nibbles):
    N3, N2, N1, N0 = nibbles
    val = ((N3 & 0xF) << 12) | ((N2 & 0xF) << 8) | ((N1 & 0xF) << 4) | (N0 & 0xF)
    return val

def generate_move_table():
    moves = np.zeros(65536, dtype=np.uint16)
    for i in range(65536):
        if(i%50==0):
            print(i)
        vec = [0 if x==0 else 2**x for x in extract_nibbles(i)]
        updated_vec = collapse_right(vec)
        nibbles = [0 if x==0 else int(np.log2(x)) for x in updated_vec]
        moves[i] = pack_nibbles(nibbles)

if __name__ == "__main__":
    generate_move_table()
    print(extract_nibbles(1500))
# Even better simplification

# You may not need this table at all.

# While building your move LUT:

# can_left  = (new_row_left  != row)
# can_right = (new_row_right != row)

# So you can store:

# move_table_left[row]
# move_table_right[row]

# and infer legality via comparison.