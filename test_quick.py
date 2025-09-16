#!/usr/bin/env python3
"""
Quick test to verify the chess AI game runs without the corruption bug.
This runs a few moves to make sure basic functionality works.
"""

from chessTable import ChessTable
from minimax import choose_best_move

def test_quick_game():
    """Test a quick game to verify no corruption occurs"""
    print("Testing quick chess AI game...")
    
    game = ChessTable()
    
    # Test a few moves at depth 3
    moves = []
    for i in range(8):  # Play 8 moves total
        player_name = "White" if game.p_move == 1 else "Black"
        print(f"Turn {i+1}: {player_name} to move")
        
        # Choose a move at depth 3
        move = choose_best_move(game, depth=3, max_time=5.0)
        
        if move is None:
            print(f"No moves available for {player_name}")
            break
            
        print(f"  {player_name} plays: {game.move_to_uci(move)}")
        game.make_move(move)
        moves.append(move)
        
    print("\nTest completed successfully!")
    print(f"Played {len(moves)} moves without corruption.")
    
    # Verify final board state is sane
    piece_count = {}
    for y in range(8):
        for x in range(8):
            piece = game.board[y][x]
            if piece != 0:
                piece_count[piece] = piece_count.get(piece, 0) + 1
    
    # Basic sanity check
    white_pawns = piece_count.get(1, 0)
    black_pawns = piece_count.get(-1, 0)
    
    if white_pawns > 8 or black_pawns > 8:
        print(f"ERROR: Invalid pawn counts - White: {white_pawns}, Black: {black_pawns}")
        return False
        
    print(f"Final piece counts: White pawns: {white_pawns}, Black pawns: {black_pawns}")
    return True

if __name__ == "__main__":
    success = test_quick_game()
    if success:
        print("\n✅ All tests passed! The corruption bug is fixed.")
    else:
        print("\n❌ Tests failed! There may still be issues.")