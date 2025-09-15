# @title Minimax

import math
import random
from copy import deepcopy

def choose_best_move(game, depth=3):
    """
    Retorna a melhor jogada usando Minimax com poda alfa-beta
    """
    _, best_move = minimax(game, depth, -math.inf, math.inf, True)
    return best_move

def minimax(game, depth, alpha, beta, maximizing_player):
    """
    Minimax com poda alfa-beta e detecção de cheque-mate / afogamento.
    """
    legal_moves = game.generate_legal_moves(game.p_move)
    if not legal_moves:
        if game.is_in_check(game.p_move):
            return (-9999 if maximizing_player else 9999), None
        else:
            return 0, None  # empate por afogamento

    if depth == 0:
        return game.evaluate(), None

    best_moves = []

    if maximizing_player:
        max_eval = -math.inf
        for move in legal_moves:
            g_copy = deepcopy(game)
            g_copy.make_move(move)
            eval_score, _ = minimax(g_copy, depth-1, alpha, beta, False)
            if eval_score > max_eval:
                max_eval = eval_score
                best_moves = [move]
            elif eval_score == max_eval:
                best_moves.append(move)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, random.choice(best_moves)
    else:
        min_eval = math.inf
        for move in legal_moves:
            g_copy = deepcopy(game)
            g_copy.make_move(move)
            eval_score, _ = minimax(g_copy, depth-1, alpha, beta, True)
            if eval_score < min_eval:
                min_eval = eval_score
                best_moves = [move]
            elif eval_score == min_eval:
                best_moves.append(move)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, random.choice(best_moves)