"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    cnt = 0
    for row in board:
        for ceil in row:
            if ceil == EMPTY:
                cnt += 1

    cnt = len(board[0]) * len(board) - cnt
    return ["X", "O"][cnt % 2]

    raise NotImplementedError


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    set_actions = set()
    for i, row in enumerate(board):
        for j, ceil in enumerate(row):
            if ceil == EMPTY:
                set_actions.add((i, j))
    return set_actions
    raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    n_board = copy.deepcopy(board)
    name_player = player(n_board)
    (i, j) = action
    if n_board[i][j] == EMPTY:
        n_board[i][j] = name_player
    else:
        raise Exception("NonValid Action")
    return n_board
    raise NotImplementedError


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    list_players = ["X", "O"]
    for name_player in list_players:
        list_check = []
        # check_row
        for row in board:
            list_check.append(all([ceil == name_player for ceil in row]))
        # check_col
        for n_col in range(len(board[0])):
            list_check.append(
                all([row[n_col] == name_player for row in board]))
        # check diagonal 3 x 3
        diagonal_1 = [board[0][0], board[1][1], board[2][2]]
        list_check.append(all([ceil == name_player for ceil in diagonal_1]))

        diagonal_2 = [board[0][2], board[1][1], board[2][0]]
        list_check.append(all([ceil == name_player for ceil in diagonal_2]))

        if(any(list_check)):
            return name_player
    return None
    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    cnt = 0
    for row in board:
        for ceil in row:
            if ceil == EMPTY:
                cnt += 1

    return cnt == 0 or (winner(board) != None)
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if terminal(board):
        utility_list = {"X": 1, "O": -1, None: 0}
        return utility_list[winner(board)]
    else:
        raise Exception("The Game has not ended")

    raise NotImplementedError


def optimal(board, alpha, beta):

    name_player = player(board)
    if(terminal(board)):
        return utility(board)

    if name_player == "X":
        max_utility = -2
        for action in actions(board):
            n_board = result(board, action)
            n_alpha = alpha
            n_beta = beta

            max_utility = max(max_utility, optimal(n_board, n_alpha, n_beta))

            alpha = max(alpha, max_utility)

            if beta <= alpha:
                break

        return max_utility
    else:
        min_utility = 2
        for action in actions(board):
            n_board = result(board, action)
            n_alpha = alpha
            n_beta = beta

            min_utility = min(min_utility, optimal(n_board, n_alpha, n_beta))

            beta = min(beta, min_utility)
            if beta <= alpha:
                break

        return min_utility


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    name_player = player(board)
    optimal_action = (0, 0)

    if name_player == "X":
        optimal_utility = -2

        for action in actions(board):
            n_board = result(board, action)
            cur_ultility = optimal(n_board, -2, 2)

            if cur_ultility > optimal_utility:
                optimal_action = action
                optimal_utility = cur_ultility
    else:
        optimal_utility = 2

        for action in actions(board):
            n_board = result(board, action)
            cur_ultility = optimal(n_board, -2, 2)

            if cur_ultility < optimal_utility:
                optimal_action = action
                optimal_utility = cur_ultility

    return optimal_action

    raise NotImplementedError
