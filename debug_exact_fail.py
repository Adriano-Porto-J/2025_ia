#!/usr/bin/env python3

from chessTable import ChessTable
from minimax import choose_best_move

def setup_exact_failing_position():
    """Set up the exact board position from the failing game at Turn 11"""
    game = ChessTable()
    
    # Replay the exact moves from the failing game
    moves_sequence = [
        "d2d4",    # Turn 0: White d2d4  
        "d7d5",    # Turn 1: Black d7d5
        "a2a4",    # Turn 2: White a2a4
        "g7g5",    # Turn 3: Black g7g5
        "e1d2",    # Turn 4: White e1d2
        "a7a5",    # Turn 5: Black a7a5
        "f2f4",    # Turn 6: White f2f4
        "a8a7",    # Turn 7: Black a8a7
        "g2g4",    # Turn 8: White g2g4
        "c7c5",    # Turn 9: Black c7c5
        "b2b4",    # Turn 10: White b2b4
    ]
    
    for i, move_str in enumerate(moves_sequence):
        # Parse move string (e.g., "d2d4" -> ((3,6), (3,4), None))
        fx, fy = game.x.index(move_str[0]), game.y.index(move_str[1])
        tx, ty = game.x.index(move_str[2]), game.y.index(move_str[3])
        move = ((fx, fy), (tx, ty), None)
        
        print(f"Move {i}: {move_str} -> {move}")
        print(f"Current player: {game.p_move}")
        
        # Validate and make the move
        try:
            game.make_move(move)
            print(f"Move {i} successful")
        except Exception as e:
            print(f"ERROR in move {i}: {e}")
            break
        
        print(f"New player: {game.p_move}")
        print()
    
    return game

def detailed_minimax_debug(game):
    """Debug minimax step by step"""
    print("=== DETAILED MINIMAX DEBUG ===")
    game.display()
    print(f"Current player: {game.p_move}")
    
    # Get legal moves
    legal_moves = game.generate_legal_moves(game.p_move)
    print(f"Legal moves: {len(legal_moves)}")
    
    # Test each move manually first
    print("\n=== Testing each legal move ===")
    for i, move in enumerate(legal_moves[:10]):
        (fx, fy), (tx, ty), promotion = move
        moved_piece = game.board[fy][fx]
        captured_piece = game.board[ty][tx]
        
        print(f"\nMove {i}: {game.square_to_algebraic((fx,fy))}{game.square_to_algebraic((tx,ty))}")
        print(f"  Moved: {moved_piece}, Captured: {captured_piece}, Current player: {game.p_move}")
        
        # Manual validation check
        if captured_piece != 0:
            is_own_piece = ((captured_piece > 0 and game.p_move == 1) or (captured_piece < 0 and game.p_move == -1))
            print(f"  Own piece validation: captured={captured_piece}, p_move={game.p_move}, is_own={is_own_piece}")
        
        # Try to make/undo the move
        try:
            # Save state
            old_state = game.get_state()
            old_p_move = game.p_move
            
            # Set search mode
            game._in_search = True
            
            # Make move
            game.make_move(move)
            print(f"  Move made successfully, new player: {game.p_move}")
            
            # Undo move
            game.undo_move()
            print(f"  Move undone successfully, restored player: {game.p_move}")
            
            # Verify state restoration
            if game.p_move != old_p_move:
                print(f"  ERROR: Player not restored! Expected {old_p_move}, got {game.p_move}")
            if game.get_state() != old_state:
                print(f"  ERROR: State not fully restored!")
                
            # Clear search mode
            game._in_search = False
            
        except Exception as e:
            print(f"  ERROR making/undoing move: {e}")
            print(f"  Current player when error: {game.p_move}")
            
            # Show problematic move details
            print(f"  Move details: from {(fx,fy)} to {(tx,ty)}")
            print(f"  Board at from: {game.board[fy][fx]}")
            print(f"  Board at to: {game.board[ty][tx]}")
            
            return move, e
    
    return None, None

def main():
    # Set up the exact failing position
    game = setup_exact_failing_position()
    
    print("\n" + "="*50)
    print("FINAL BOARD POSITION (Turn 11 - Black to move)")
    print("="*50)
    
    # Debug the problematic move
    problem_move, error = detailed_minimax_debug(game)
    
    if problem_move:
        print(f"\nFound problematic move: {problem_move}")
        print(f"Error: {error}")
    else:
        print("\nNo issues found with individual moves, trying minimax...")
        
        # Try actual minimax
        try:
            print("\n=== TRYING MINIMAX SEARCH ===")
            game._in_search = False  # Make sure we're not in search mode
            best_move = choose_best_move(game, depth=3, max_time=5.0)
            print(f"Minimax succeeded: {best_move}")
        except Exception as e:
            print(f"Minimax failed: {e}")
            print(f"Game state when failed:")
            print(f"  p_move: {game.p_move}")
            print(f"  _in_search: {getattr(game, '_in_search', 'NOT_SET')}")

if __name__ == "__main__":
    main()