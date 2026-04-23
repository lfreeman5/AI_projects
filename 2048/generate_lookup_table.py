from utilities import collapse_right

def extract_nibbles(x: int) -> list[int]:
    # x between 0 and 65536, returns 4 bits
    return [
        int((x >> 12) & 0xF),  # highest 4 bits
        int((x >> 8)  & 0xF),
        int((x >> 4)  & 0xF),
        int(x & 0xF)           # lowest 4 bits
    ]

def pack_nibbles(nibbles: list[int]) -> int:
    N3, N2, N1, N0 = nibbles
    val = ((N3 & 0xF) << 12) | ((N2 & 0xF) << 8) | ((N1 & 0xF) << 4) | (N0 & 0xF)
    return int(val)

def reverse_row(row: int) -> int:
    return int(
        ((row & 0x000F) << 12)
      | ((row & 0x00F0) << 4)
      | ((row & 0x0F00) >> 4)
      | ((row & 0xF000) >> 12)
    )

def generate_move_tables() -> tuple[list[int], list[int], list[int], list[int]]:
    moves_right = [0]*65536
    moves_left = [0]*65536
    added_score_left = [0]*65536
    added_score_right = [0]*65536
    for i in range(65536):
        vec = extract_nibbles(i)
        updated_vec, added_score = collapse_right(vec)
        moves_right[i] = pack_nibbles(updated_vec)
        added_score_right[i] = added_score

        # make left moves
        reversed_row = reverse_row(i)
        vec = extract_nibbles(reversed_row)
        updated_vec, added_score = collapse_right(vec)
        moves_left[i] = reverse_row(pack_nibbles(updated_vec))
        added_score_left[i] = added_score

    return moves_left, moves_right, added_score_left, added_score_right

def generate_max_tile_table() -> list[int]:
    max_score = [0]*65536
    for i in range(65536):
        max_score[i] = max([0 if x == 0 else 2**x for x in extract_nibbles(i)])
    return max_score


def generate_possible_tables(moves_left: list[int], moves_right: list[int]) -> tuple[list[bool], list[bool]]:
    move_left = [False]*65536
    move_right = [False]*65536
    for i in range(65536):
        move_left[i] = moves_left[i] != i
        move_right[i] = moves_right[i] != i
    return move_left, move_right


def generate_lookup_tables_dict() -> dict[str, list]:
    move_left, move_right, added_left, added_right = generate_move_tables()
    can_left, can_right = generate_possible_tables(move_left, move_right)
    return {
        'move_left': move_left,
        'move_right': move_right,
        'added_left': added_left,
        'added_right': added_right,
        'can_left': can_left,
        'can_right': can_right,
    }

