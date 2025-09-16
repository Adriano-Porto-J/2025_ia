#!/usr/bin/env python3

import sys
from chessTable import ChessTable
from minimax import choose_best_move

def test_ai_vs_ai_depth_3():
    """Reproduce the AI vs AI game with depth 3 to find the bug"""
    game = ChessTable()
    
    for turn in range(20):  # Test first 20 turns
        print(f"\nTurno {turn}: Jogador {'Brancas' if game.p_move == 1 else 'Pretas'} pensando...")
        game.display()
        
        # Check for invalid moves in current position
        moves = game.generate_pseudo_legal_moves(game.p_move)
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
            print(f"ERROR: Found {len(invalid_moves)} invalid moves in position!")
            for move, moved, target in invalid_moves[:3]:  # Show first 3
                (fx, fy), (tx, ty), promotion = move
                print(f"  {game.square_to_algebraic((fx,fy))}{game.square_to_algebraic((tx,ty))}: moved={moved}, target={target}")
            break
        
        try:
            # Use depth 3 like in the failing case
            move = choose_best_move(game, depth=3, max_time=3.0)
            if not move:
                print("No move found!")
                break
                
            # Validate the move before making it
            (fx, fy), (tx, ty), promotion = move
            moved_piece = game.board[fy][fx]
            target_piece = game.board[ty][tx]
            
            print(f"Attempting move: {game.square_to_algebraic((fx,fy))}{game.square_to_algebraic((tx,ty))}")
            print(f"  Moving piece: {moved_piece}, Target: {target_piece}")
            
            if target_piece != 0 and ((moved_piece > 0 and target_piece > 0) or (moved_piece < 0 and target_piece < 0)):
                print(f"ERROR: AI chose invalid move - trying to capture own piece!")
                print(f"  Player: {game.p_move}, Moved: {moved_piece}, Target: {target_piece}")
                break
            
            game.make_move(move)
            print(f"Move successful: {game.square_to_algebraic((fx,fy))}{game.square_to_algebraic((tx,ty))}")
            
        except Exception as e:
            print(f"Error on turn {turn}: {e}")
            print(f"Current player: {game.p_move}")
            
            # Debug: show last generated moves
            print("Last generated moves:")
            moves = game.generate_pseudo_legal_moves(game.p_move)
            for i, move in enumerate(moves[:10]):
                (fx, fy), (tx, ty), promotion = move
                moved_piece = game.board[fy][fx]
                target_piece = game.board[ty][tx]
                invalid = ""
                if target_piece != 0 and ((moved_piece > 0 and target_piece > 0) or (moved_piece < 0 and target_piece < 0)):
                    invalid = " [INVALID!]"
                print(f"  {i}: {game.square_to_algebraic((fx,fy))}{game.square_to_algebraic((tx,ty))} (moved={moved_piece}, target={target_piece}){invalid}")
            break

if __name__ == "__main__":
    test_ai_vs_ai_depth_3()