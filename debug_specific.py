#!/usr/bin/env python3

from chessTable import ChessTable
from minimax import choose_best_move

def setup_failing_position():
    """Set up the board position from the failing game"""
    game = ChessTable()
    
    # Replay the moves from the failing game
    moves_sequence = [
        "d2d4",    # Turn 0: White d2d4  
        "e7e5",    # Turn 1: Black e7e5
        "c1g5",    # Turn 2: White c1g5
        "f7f5",    # Turn 3: Black f7f5
        "b2b4",    # Turn 4: White b2b4
        "b7b5",    # Turn 5: Black b7b5
        "a1a3",    # Turn 6: White a1a3
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

def debug_validation_issue():
    """Debug the specific validation issue"""
    game = setup_failing_position()
    
    print("Final position:")
    game.display()
    print(f"Current player: {game.p_move}")
    
    # Generate moves for the current player
    print("\n=== Generating legal moves ===")
    legal_moves = game.generate_legal_moves(game.p_move)
    print(f"Found {len(legal_moves)} legal moves")
    
    # Test each move to see if any cause the validation error
    print("\n=== Testing moves ===")
    for i, move in enumerate(legal_moves[:10]):  # Test first 10
        (fx, fy), (tx, ty), promotion = move
        moved_piece = game.board[fy][fx]
        captured_piece = game.board[ty][tx]
        
        print(f"Move {i}: {game.square_to_algebraic((fx,fy))}{game.square_to_algebraic((tx,ty))}")
        print(f"  Moved: {moved_piece}, Captured: {captured_piece}")
        
        # Test the validation manually
        if captured_piece != 0:
            is_own_piece = ((captured_piece > 0 and game.p_move == 1) or (captured_piece < 0 and game.p_move == -1))
            print(f"  Own piece check: captured={captured_piece}, p_move={game.p_move}, is_own={is_own_piece}")
        
        # Try to make the move
        try:
            # Store state
            old_p_move = game.p_move
            old_board = [row[:] for row in game.board]
            
            game.make_move(move)
            print(f"  Move successful")
            game.undo_move()
            
            # Verify state restoration
            if game.p_move != old_p_move:
                print(f"  ERROR: p_move not restored! Expected {old_p_move}, got {game.p_move}")
            if game.board != old_board:
                print(f"  ERROR: Board not restored properly!")
                
        except Exception as e:
            print(f"  ERROR: {e}")
            break
    
    # Try the minimax search at different depths
    print("\n=== Testing minimax search ===")
    for depth in [2, 3]:
        print(f"\n--- Depth {depth} ---")
        try:
            best_move = choose_best_move(game, depth=depth, max_time=5.0)
            print(f"Minimax depth {depth} returned: {best_move}")
        except Exception as e:
            print(f"Minimax depth {depth} failed: {e}")
            # If it fails, let's debug the state
            print(f"Current player when failed: {game.p_move}")
            game.display()
            break

if __name__ == "__main__":
    debug_validation_issue()