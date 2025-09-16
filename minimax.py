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
    
    # Store initial game state to detect corruption
    initial_player = game.p_move
    initial_board_hash = hash(str(game.board))
    
    # Clear transposition table periodically to avoid memory issues
    if len(transposition_table) > 50000:  # Allow larger cache for better performance
        transposition_table.clear()
    
    # Get legal moves at start and use as fallback
    legal_moves = game.generate_legal_moves(game.p_move)
    if not legal_moves:
        game._in_search = False
        return None
    
    # If no time limit, use regular minimax
    if max_time is None:
        # maximizing_player should match the current player: True for White (1), False for Black (-1)
        initial_maximizing = (game.p_move == 1)
        _, best_move = minimax(game, depth, -math.inf, math.inf, initial_maximizing)
        
        # Validate game state wasn't corrupted during search
        if game.p_move != initial_player:
            print(f"ERROR: Game state corrupted during search - player changed from {initial_player} to {game.p_move}")
            game.p_move = initial_player  # Restore correct player
        
        final_board_hash = hash(str(game.board))
        if final_board_hash != initial_board_hash:
            print(f"ERROR: Board state corrupted during search - hash changed")
        
        # Final validation: ensure the returned move is actually legal
        if best_move is not None and best_move in legal_moves:
            # Clear search mode flag and clean up search state
            game._in_search = False
            if hasattr(game, 'search_log'):
                if len(game.search_log) > 0:
                    print(f"WARNING: Search log not empty after non-timed search: {len(game.search_log)} moves left")
                game.search_log = []
            if hasattr(game, '_search_depth'):
                if game._search_depth != 0:
                    print(f"WARNING: Search depth counter not zero after non-timed search: {game._search_depth}")
                game._search_depth = 0
            return best_move
        else:
            if best_move is not None:
                print(f"Warning: Minimax returned illegal move {best_move}, falling back to first legal move")
            # Clear search mode flag and clean up search state
            game._in_search = False
            if hasattr(game, 'search_log'):
                game.search_log = []
            if hasattr(game, '_search_depth'):
                game._search_depth = 0
            return legal_moves[0]
    
    # Iterative deepening com limite de tempo
    # Clear transposition table for timed searches to prevent corruption
    transposition_table.clear()
    
    # Use the legal moves we already generated
    best_move = legal_moves[0]  # Safe fallback - always use first legal move
    completed_depth = 0
    
    for current_depth in range(1, depth + 1):
        # Conservative time check before starting new depth
        elapsed = time.time() - search_start_time
        # Use more time for first few depths, then be more conservative
        time_threshold = max_time * (0.7 if current_depth <= 2 else 0.4)
        if elapsed > time_threshold:
            break
            
        # Try this depth level with timeout protection
        try:
            # maximizing_player should match the current player: True for White (1), False for Black (-1)
            initial_maximizing = (game.p_move == 1)
            _, move = minimax(game, current_depth, -math.inf, math.inf, initial_maximizing)
            
            # Validate the move before accepting it
            if move is not None and move in legal_moves:
                best_move = move
                completed_depth = current_depth
            else:
                # Invalid move returned - stop iterative deepening but keep previous best
                if move is not None:
                    print(f"Warning: Minimax depth {current_depth} returned illegal move {move}, keeping previous best")
                break
                
        except TimeoutError:
            # Timeout during this depth - keep the best move from previous completed depth
            # Force cleanup of any incomplete search state
            while hasattr(game, 'search_log') and len(game.search_log) > 0:
                try:
                    game.undo_move()
                except:
                    break
            break
        except Exception as e:
            # Any other error - stop and keep previous best move
            print(f"Warning: Error during minimax depth {current_depth}: {e}, keeping previous best")
            # Force cleanup of any incomplete search state
            while hasattr(game, 'search_log') and len(game.search_log) > 0:
                try:
                    game.undo_move()
                except:
                    break
            break
    
    # Store the actual depth reached for debugging
    global actual_depth_reached
    actual_depth_reached = completed_depth
    
    # Validate game state wasn't corrupted during iterative deepening search
    if game.p_move != initial_player:
        print(f"ERROR: Game state corrupted during iterative search - player changed from {initial_player} to {game.p_move}")
        game.p_move = initial_player  # Restore correct player
    
    final_board_hash = hash(str(game.board))
    if final_board_hash != initial_board_hash:
        print(f"ERROR: Board state corrupted during iterative search - hash changed")
    
    # Clear search mode flag and clean up search state
    game._in_search = False
    # Force cleanup of any remaining moves in search log
    if hasattr(game, 'search_log'):
        if len(game.search_log) > 0:
            print(f"WARNING: Search log not empty after search: {len(game.search_log)} moves left - forcing cleanup")
            # Try to undo remaining moves
            while len(game.search_log) > 0:
                try:
                    game.undo_move()
                except:
                    # If undo fails, just clear the log
                    break
        game.search_log = []
    if hasattr(game, '_search_depth'):
        if game._search_depth != 0:
            print(f"WARNING: Search depth counter not zero after search: {game._search_depth}")
        game._search_depth = 0
    
    # Final validation: ensure the returned move is actually legal
    if best_move is not None and best_move in legal_moves:
        return best_move
    else:
        # This should never happen now, but safety check
        print(f"Warning: Final move validation failed, using first legal move")
        return legal_moves[0]

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
    
    # Transposition table temporarily disabled to prevent corruption issues
    # TODO: Fix state key generation and re-enable caching
    position_key = None
    
    # Important: Generate moves for the CURRENT player, not based on maximizing_player
    # The maximizing_player parameter is for evaluation direction, not move generation
    legal_moves = game.generate_legal_moves(game.p_move)
    if not legal_moves:
        if game.is_in_check(game.p_move):
            eval_score = -9999 if maximizing_player else 9999
        else:
            eval_score = 0  # empate por afogamento
        # transposition_table[position_key] = eval_score  # Disabled
        return eval_score, None

    if depth == 0:
        eval_score = game.evaluate()
        # Transposition table disabled
        # try:
        #     transposition_table[position_key] = eval_score
        # except:
        #     pass  # Skip caching if key generation fails
        return eval_score, None

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
                
        # Transposition table disabled
        # transposition_table[position_key] = max_eval
        
        # Return both evaluation and selected move
        selected_move = random.choice(best_moves)
        
        # Additional safety check: ensure the selected move belongs to current player
        if selected_move is not None:
            fx, fy = selected_move[0]
            if 0 <= fy < 8 and 0 <= fx < 8:  # Bounds check
                piece_at_source = game.board[fy][fx]
                # Verify piece belongs to current player
                if piece_at_source == 0:
                    print(f"Error: Minimax trying to move from empty square ({fx},{fy}) for player {game.p_move}")
                    return max_eval, None
                elif (piece_at_source > 0 and game.p_move != 1) or (piece_at_source < 0 and game.p_move != -1):
                    print(f"Error: Minimax trying to move opponent's piece {piece_at_source} for player {game.p_move}")
                    return max_eval, None
            else:
                print(f"Error: Minimax returned out-of-bounds move {selected_move}")
                return max_eval, None
        
        return max_eval, selected_move
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
                
        # Transposition table disabled
        # transposition_table[position_key] = min_eval
        
        # Return both evaluation and selected move
        selected_move = random.choice(best_moves)
        
        # Additional safety check: ensure the selected move belongs to current player
        if selected_move is not None:
            fx, fy = selected_move[0]
            if 0 <= fy < 8 and 0 <= fx < 8:  # Bounds check
                piece_at_source = game.board[fy][fx]
                # Verify piece belongs to current player
                if piece_at_source == 0:
                    print(f"Error: Minimax trying to move from empty square ({fx},{fy}) for player {game.p_move}")
                    return min_eval, None
                elif (piece_at_source > 0 and game.p_move != 1) or (piece_at_source < 0 and game.p_move != -1):
                    print(f"Error: Minimax trying to move opponent's piece {piece_at_source} for player {game.p_move}")
                    return min_eval, None
            else:
                print(f"Error: Minimax returned out-of-bounds move {selected_move}")
                return min_eval, None
        
        return min_eval, selected_move
