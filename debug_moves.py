#!/usr/bin/env python3

from chessTable import ChessTable

def test_move_generation():
    game = ChessTable()
    print("Initial board:")
    game.display()
    
    print("Current player:", game.p_move)
    
    # Generate moves
    moves = game.generate_pseudo_legal_moves(game.p_move)
    print(f"Generated {len(moves)} moves")
    
    # Check for invalid moves (capturing own pieces)
    invalid_moves = []
    for move in moves:
        (fx, fy), (tx, ty), promotion = move
        moved_piece = game.board[fy][fx]  
        target_piece = game.board[ty][tx]
        
        # Check if we're trying to capture our own piece
        if target_piece != 0:
            if (moved_piece > 0 and target_piece > 0) or (moved_piece < 0 and target_piece < 0):
                invalid_moves.append((move, moved_piece, target_piece))
    
    if invalid_moves:
        print(f"Found {len(invalid_moves)} invalid moves (capturing own pieces):")
        for move, moved, target in invalid_moves[:5]:  # Show first 5
            (fx, fy), (tx, ty), promotion = move
            print(f"  {game.square_to_algebraic((fx,fy))}{game.square_to_algebraic((tx,ty))}: moved={moved}, target={target}")
    else:
        print("No invalid moves found!")
    
    # Test a specific move that might be problematic
    print("\nTesting individual piece moves:")
    for y in range(8):
        for x in range(8):
            piece = game.board[y][x]
            if piece != 0 and ((piece > 0 and game.p_move == 1) or (piece < 0 and game.p_move == -1)):
                piece_type = abs(piece)
                moves_for_piece = game.get_piece_moves_fast(piece_type, game.p_move, (x, y))
                
                for dest in moves_for_piece:
                    dest_piece = game.board[dest[1]][dest[0]]
                    if dest_piece != 0 and ((dest_piece > 0 and game.p_move == 1) or (dest_piece < 0 and game.p_move == -1)):
                        print(f"PROBLEM: {game.square_to_algebraic((x,y))} -> {game.square_to_algebraic(dest)}")
                        print(f"  Piece {piece} trying to capture own piece {dest_piece}")
                        break

if __name__ == "__main__":
    test_move_generation()