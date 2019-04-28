#!/usr/bin/python3

import time
import random

"""
This file contains all Abstract Player classes but no actual finished Implementations.
The Finished Implementations can be cound in the file implementations.py
"""


class Player:
    """[Abstract] Base Class for a Connect4 Player"""
    IS_HUMAN = False

    def __init__(self, color, params):
        self.color = color
        self.params = params
        if params.timeout is not None:
            self.timeout = params.timeout
        else:
            self.timeout = 0xdeadbeef

    def next_move(self, gb):
        """Takes a game board and returns the next move"""
        raise NotImplementedError("Please Implement this method")

    def get_name(self):
        """Returns Name of this player"""
        return self.__class__.__name__


class HumanPlayer(Player):
    """Human Player that lets user choose where to play"""
    IS_HUMAN = True

    def next_move(self, gb):
        while True:
            move_raw = input("Player {}, were do you want to move next? ".format(gb.get_occupation_string(self.color)))
            if move_raw == "exit":
                exit(0)
            try:
                move = int(move_raw)
            except ValueError:
                print("Please enter an Integer.")
                continue
            if not gb.is_legal(move):
                print("You can't play there.")
            else:
                # gb = gb.clone()
                # gb.place_stone(move, self.color)
                # print(gb)
                # p = SimplePlayer(gb.other_player(self.color), self.params)
                # print("SCORE:", p.score(gb, 5))
                return move


class TimedPlayer(Player):
    """[Abstract] Base Class for plaers with time limits"""
    SAFETY_FACTOR = .95

    def next_move(self, gb):
        timeout = time.time() + self.timeout * self.SAFETY_FACTOR
        move = 0
        try:
            for depth in range(gb.ROWS * gb.COLS):
                move = self.next_move_timeout(gb, depth, timeout)
        except TimeoutError:
            pass
        return move

    def next_move_timeout(self, gb, depth, timeout):
        """Tries to calculate best move within a certain timeout. If timeout is reached before,
        a timeout exception gets thrown."""
        raise NotImplementedError("Please Implement this method")


class DepthPlayer(TimedPlayer):
    """[Abstract] Base Class for players that always have the same serach depth (useful for debugging)"""
    DEPTH = 6

    def next_move(self, gb):
        timeout = time.time() + 100
        move = self.next_move_timeout(gb, self.DEPTH, timeout)
        return move


class AlphaBetaPlayer(TimedPlayer):
    """[Abstract] Alpha Beta Player - Uses Alpha Beta Algorithm to evaluate Game Tree"""
    POSITION_ORDER = [3, 2, 4, 5, 1, 0, 6]
    WIN_SCORE = 1000

    ALPHA_INIT = -0xfffffff0
    BETA_INIT = 0xfffffff0

    def next_move_timeout(self, gb, depth, timeout):
        player = self.color  # gb.other_player(self.color)
        alpha = self.ALPHA_INIT
        beta = self.BETA_INIT

        clone = gb.clone()
        bestMove = -1

        for pos in self.POSITION_ORDER:
            if clone.place_stone(pos, player):
                score = self.min(clone, depth - 1, alpha, beta, timeout)
                if score > alpha:
                    alpha = score
                    bestMove = pos
                clone = gb.clone()
        return bestMove

    def min(self, gb, depth, alpha, beta, timeout):
        if gb.has_won(self.color):
            return self.WIN_SCORE * (depth + 1)
        elif timeout < time.time():
            raise TimeoutError()
        elif depth <= 0:
            return self.score(gb, depth)

        clone = gb.clone()

        for pos in self.POSITION_ORDER:
            if clone.place_stone(pos, gb.other_player(self.color)):
                score = self.max(clone, depth - 1, alpha, beta, timeout)
                if score < beta:
                    beta = score
                if alpha >= beta:
                    return beta
                clone = gb.clone()
        return beta

    def max(self, gb, depth, alpha, beta, timeout):
        if gb.has_won(gb.other_player(self.color)):
            return - self.WIN_SCORE * (depth + 1)
        elif timeout < time.time():
            raise TimeoutError()
        elif depth <= 0:
            return self.score(gb, depth)

        clone = gb.clone()

        for pos in self.POSITION_ORDER:
            if clone.place_stone(pos, self.color):
                score = self.min(clone, depth - 1, alpha, beta, timeout)
                if score > alpha:
                    alpha = score
                if alpha >= beta:
                    return alpha
                clone = gb.clone()
        return alpha

    def score(self, gb, depth):
        """Gives a score to a given position."""
        raise NotImplementedError("Please Implement this method")


class RandomizedAlphaBetaPlayer(AlphaBetaPlayer):
    """[Abstract] Uses Alpha Beta Player but randomizes search order sligtly.
    Prevents Player from always playing in the center row."""
    POSITION_ORDER_BASE = [3, 2, 4, 5, 1, 0, 6]
    POSITION_ORDER = [3, 2, 4, 5, 1, 0, 6]
    RANDOMNESS = .3
    random.seed(0)

    def random_order(self):
        for i in range(len(self.POSITION_ORDER_BASE)):
            self.POSITION_ORDER[i] = self.POSITION_ORDER_BASE[i]

        for i in range(len(self.POSITION_ORDER_BASE) - 1):
            if random.random() < self.RANDOMNESS:
                temp = self.POSITION_ORDER[i]
                self.POSITION_ORDER[i] = self.POSITION_ORDER[i + 1]
                self.POSITION_ORDER[i + 1] = temp

    def next_move_timeout(self, gb, depth, timeout):
        self.random_order()  # Randomize order before every move
        return super().next_move_timeout(gb, depth, timeout)


class HashedPlayer(RandomizedAlphaBetaPlayer):
    MIN_HASH_DEPTH = 0

    def next_move_timeout(self, gb, depth, timeout):
        self.hash_map = []
        for i in range(depth + 1):
            self.hash_map.append({})
        return super().next_move_timeout(gb, depth, timeout)

    def min(self, gb, depth, alpha, beta, timeout):
        if depth >= self.MIN_HASH_DEPTH:
            if gb in self.hash_map[depth]:
                return self.hash_map[depth][gb]
            else:
                score = super().min(gb, depth, alpha, beta, timeout)
                self.hash_map[depth][gb] = score
                return score
        else:
            return super().min(gb, depth, alpha, beta, timeout)

    def max(self, gb, depth, alpha, beta, timeout):
        if depth >= self.MIN_HASH_DEPTH:
            if gb in self.hash_map[depth]:
                return self.hash_map[depth][gb]
            else:
                score = super().max(gb, depth, alpha, beta, timeout)
                self.hash_map[depth][gb] = score
                return score
        else:
            return super().max(gb, depth, alpha, beta, timeout)