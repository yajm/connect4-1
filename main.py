#!/usr/bin/python3

if __name__ == "__main__":
    from arena import Arena, GameParameters
    from gameboard import BasicGameBoard, BitBoard7x6
    from player import *

    arena = Arena()

    params = GameParameters(timeout=1)

    outcome = arena.play_game(StrategyChangePlayer HumanPlayer, BitBoard7x6, params)

    print("\nGAME FINISHED - {}:\n{}".format(outcome, outcome.gb))
