#!/usr/bin/env python3

from chessTable import ChessTable
from minimax import choose_best_move

def setup_new_failing_position():
    """Set up the new failing position"""
    game = ChessTable()
    
    # Replay the exact moves from the failing game
    moves_sequence = [
        "d2d4",    # Turn 0: White d2d4  
        "b8c6",    # Turn 1: Black b8c6
        "b2b4",    # Turn 2: White b2b4
        "c6b4",    # Turn 3: Black c6b4 (captures white pawn)
    ]
    
    for i, move_str in enumerate(moves_sequence):
        # Parse move string 
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
        game.display()
        print()
    
    return game

def main():
    game = setup_new_failing_position()
    
    print("=== FINAL POSITION (Turn 4 - White to move) ===")
    print(f"Current player: {game.p_move}")
    
    # Test minimax
    try:
        best_move = choose_best_move(game, depth=3, max_time=5.0)
        print(f"Minimax succeeded: {best_move}")
    except Exception as e:
        print(f"Minimax failed: {e}")
        print(f"Current player when failed: {game.p_move}")

if __name__ == "__main__":
    main()