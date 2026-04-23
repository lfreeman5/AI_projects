import time
from generate_lookup_table import generate_lookup_tables_dict
from utilities import play_random_game

if __name__ == "__main__":
    lut = generate_lookup_tables_dict()
    play_random_game(lut)

    # runs = 1000
    # t0 = time.perf_counter()
    # for i in range(runs):
    #     _ = play_random_game(lut)
    #     if(i%100==0):
    #         print(_)
    # t1 = time.perf_counter()
    # total = t1 - t0
    # print(f"main_lut: ran {runs} games in {total:.4f}s, avg {total / runs:.6f}s/game")
        