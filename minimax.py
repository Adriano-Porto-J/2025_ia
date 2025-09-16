# @title Minimax

import math
import random
import time

# Tabela de transposição global para cache de avaliações de posição
transposition_table = {}
# Estatísticas de performance
nodes_searched = 0
cache_hits = 0
# Gerenciamento de tempo
search_start_time = 0
time_limit = 0
actual_depth_reached = 0
# Time check optimization - only check every N nodes
time_check_counter = 0
time_check_interval = 5  # Check time every 5 nodes (more responsive)

def order_moves(game, moves):
    """
    Order moves to improve alpha-beta pruning efficiency.
    Prioritize: high-value captures, promotions, checks, then other moves
    """
    high_value_captures = []
    low_value_captures = []
    promotions = []
    other_moves = []
    
    for move in moves:
        (fx, fy), (tx, ty), promotion = move
        
        # Prioritize promotions
        if promotion is not None:
            promotions.append(move)
            continue
            
        captured_piece = game.board[ty][tx]
        moved_piece = game.board[fy][fx]
        
        # Check if it's a capture
        if captured_piece != 0:
            # MVV-LVA: Most Valuable Victim - Least Valuable Attacker
            capture_value = abs(captured_piece) - abs(moved_piece) * 0.1
            if capture_value >= 0:  # Good capture
                high_value_captures.append(move)
            else:
                low_value_captures.append(move)
        else:
            other_moves.append(move)
    
    # Return in order of likely goodness: promotions, good captures, bad captures, other moves
    return promotions + high_value_captures + low_value_captures + other_moves

def choose_best_move(game, depth=3, max_time=None):
    """
    Retorna a melhor jogada usando Minimax com poda alfa-beta
    Com limite de tempo opcional usando iterative deepening
    """
    global nodes_searched, cache_hits, search_start_time, time_limit, time_check_counter
    
    # Reset performance counters
    nodes_searched = 0
    cache_hits = 0
    time_check_counter = 0
    search_start_time = time.time()
    time_limit = max_time
    
    # Mark game as being in search mode to skip expensive tracking
    game._in_search = True
    
    # Clear transposition table periodically to avoid memory issues
    if len(transposition_table) > 50000:  # Allow larger cache for better performance
        transposition_table.clear()
    
    # If no time limit, use regular minimax
    if max_time is None:
        # maximizing_player should match the current player: True for White (1), False for Black (-1)
        initial_maximizing = (game.p_move == 1)
        _, best_move = minimax(game, depth, -math.inf, math.inf, initial_maximizing)
        # Clear search mode flag
        game._in_search = False
        return best_move
    
    # Iterative deepening com limite de tempo
    best_move = None
    legal_moves = game.generate_legal_moves(game.p_move)
    if not legal_moves:
        return None
    
    # Começa com um movimento aleatório como fallback
    best_move = legal_moves[0]
    
    completed_depth = 0
    try:
        for current_depth in range(1, depth + 1):
            # Conservative time check before starting new depth
            elapsed = time.time() - search_start_time
            # Use more time for first few depths, then be more conservative
            time_threshold = max_time * (0.7 if current_depth <= 2 else 0.4)
            if elapsed > time_threshold:
                break
                
            # maximizing_player should match the current player: True for White (1), False for Black (-1)
            initial_maximizing = (game.p_move == 1)
            _, move = minimax(game, current_depth, -math.inf, math.inf, initial_maximizing)
            if move is not None:
                best_move = move
                completed_depth = current_depth
                
    except TimeoutError:
        # Limite de tempo excedido durante busca - retorna melhor movimento encontrado
        pass
    
    # Store the actual depth reached for debugging
    global actual_depth_reached
    actual_depth_reached = completed_depth
    
    # Clear search mode flag
    game._in_search = False
    
    return best_move

def get_search_stats():
    """
    Retorna as estatísticas da última busca
    """
    global nodes_searched, cache_hits, actual_depth_reached
    return {
        'nodes_searched': nodes_searched,
        'cache_hits': cache_hits,
        'efficiency': cache_hits/max(nodes_searched,1)*100 if nodes_searched > 0 else 0,
        'actual_depth': actual_depth_reached
    }

def minimax(game, depth, alpha, beta, maximizing_player):
    """
    Minimax com poda alfa-beta e detecção de cheque-mate / afogamento.
    """
    global nodes_searched, cache_hits, search_start_time, time_limit, time_check_counter, time_check_interval
    nodes_searched += 1
    
    # Optimized time checking - only check every N nodes to reduce overhead
    if time_limit is not None:
        time_check_counter += 1
        if time_check_counter >= time_check_interval:
            time_check_counter = 0
            elapsed = time.time() - search_start_time
            if elapsed >= time_limit * 0.95:  # Stop at 95% of time limit for safety
                raise TimeoutError("Time limit exceeded")
    
    # Check transposition table first - use fast hash instead of expensive string
    try:
        position_key = (game.get_state_hash(), depth, maximizing_player)
        if position_key in transposition_table:
            cache_hits += 1
            return transposition_table[position_key]
    except:
        # Fallback to string-based key if hash fails
        position_key = game.get_state() + str(depth) + str(maximizing_player)
        if position_key in transposition_table:
            cache_hits += 1
            return transposition_table[position_key]
    
    legal_moves = game.generate_legal_moves(game.p_move)
    if not legal_moves:
        if game.is_in_check(game.p_move):
            result = (-9999 if maximizing_player else 9999), None
        else:
            result = 0, None  # empate por afogamento
        transposition_table[position_key] = result
        return result

    if depth == 0:
        result = game.evaluate(), None
        # Store in transposition table for reuse
        try:
            transposition_table[position_key] = result
        except:
            pass  # Skip caching if key generation fails
        return result

    # Ordenação de movimentos: prioriza capturas e xeques para melhor poda
    legal_moves = order_moves(game, legal_moves)
    best_moves = []

    if maximizing_player:
        max_eval = -math.inf
        for move in legal_moves:
            # Usa make_move/undo_move ao invés de deepcopy caro
            game.make_move(move)
            eval_score, _ = minimax(game, depth-1, alpha, beta, False)
            game.undo_move()
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_moves = [move]
            elif eval_score == max_eval:
                best_moves.append(move)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        result = max_eval, random.choice(best_moves)
        transposition_table[position_key] = result
        return result
    else:
        min_eval = math.inf
        for move in legal_moves:
            # Usa make_move/undo_move ao invés de deepcopy caro
            game.make_move(move)
            eval_score, _ = minimax(game, depth-1, alpha, beta, True)
            game.undo_move()
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_moves = [move]
            elif eval_score == min_eval:
                best_moves.append(move)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        result = min_eval, random.choice(best_moves)
        transposition_table[position_key] = result
        return result