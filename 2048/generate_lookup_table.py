import numpy as np
from old import collapse_right

def extract_nibbles(x: np.uint16 | int) -> list[int]:
    # x between 0 and 65536, returns 4 bits
    x = np.uint16(x)
    return [
        int((x >> 12) & 0xF),  # highest 4 bits
        int((x >> 8)  & 0xF),
        int((x >> 4)  & 0xF),
        int(x & 0xF)           # lowest 4 bits
    ]

def pack_nibbles(nibbles: list[int]) -> np.uint16:
    N3, N2, N1, N0 = nibbles
    val = ((N3 & 0xF) << 12) | ((N2 & 0xF) << 8) | ((N1 & 0xF) << 4) | (N0 & 0xF)
    return np.uint16(val)

def reverse_row(row: np.uint16) -> np.uint16:
    return np.uint16(
        ((row & 0x000F) << 12)
      | ((row & 0x00F0) << 4)
      | ((row & 0x0F00) >> 4)
      | ((row & 0xF000) >> 12)
    )

def generate_move_tables() -> tuple[np.ndarray, np.ndarray]:
    moves_right = np.zeros(65536, dtype=np.uint16)
    moves_left = np.zeros(65536, dtype=np.uint16)
    for i in np.arange(65536, dtype=np.uint16):
        vec = [0 if x == 0 else 2**x for x in extract_nibbles(i)]
        updated_vec = collapse_right(vec)
        nibbles = [0 if x == 0 else int(np.log2(x)) for x in updated_vec]
        moves_right[i] = pack_nibbles(nibbles)

        # make left moves
        reversed_row = reverse_row(i)
        vec = [0 if x == 0 else 2**x for x in extract_nibbles(reversed_row)]
        updated_vec = collapse_right(vec)
        nibbles = [0 if x == 0 else int(np.log2(x)) for x in updated_vec]
        moves_left[i] = reverse_row(pack_nibbles(nibbles))

    return moves_left, moves_right


def generate_possible_tables(moves_left: np.ndarray, moves_right: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    move_left = np.zeros(65536, dtype=np.bool_)
    move_right = np.zeros(65536, dtype=np.bool_)
    for i in np.arange(65536, dtype=np.uint16):
        move_left[i] = moves_left[i] != i
        move_right[i] = moves_right[i] != i
    return move_left, move_right

if __name__ == "__main__":
    moves_left, moves_right = generate_move_tables()
    generate_possible_tables(moves_left, moves_right)
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