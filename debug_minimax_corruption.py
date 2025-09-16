#!/usr/bin/env python3

from chessTable import ChessTable
from minimax import choose_best_move, minimax
import math

def count_pieces(board):
    """Count all pieces on the board"""
    piece_count = {}
    for y in range(8):
        for x in range(8):
            piece = board[y][x]
            if piece != 0:
                piece_count[piece] = piece_count.get(piece, 0) + 1
    return piece_count

def validate_piece_counts(board):
    """Check if piece counts are valid"""
    counts = count_pieces(board)
    
    # Check for impossible piece counts
    issues = []
    
    # Pawns: max 8 per side (since none have been promoted yet)
    white_pawns = counts.get(1, 0)
    black_pawns = counts.get(-1, 0)
    if white_pawns > 8:
        issues.append(f"Too many white pawns: {white_pawns}")
    if black_pawns > 8:
        issues.append(f"Too many black pawns: {black_pawns}")
    
    return issues, counts

# Monkey patch the ChessTable class to add validation
original_make_move = ChessTable.make_move
original_undo_move = ChessTable.undo_move

def make_move_with_validation(self, move):
    """Make move with piece count validation"""
    
    # Count pieces before
    issues_before, counts_before = validate_piece_counts(self.board)
    
    # Call original make_move
    result = original_make_move(self, move)
    
    # Count pieces after
    issues_after, counts_after = validate_piece_counts(self.board)
    
    if issues_after:
        print(f"CORRUPTION DETECTED in make_move!")
        print(f"Move: {move}")
        print(f"Player: {self.p_move}")
        print(f"Before: {counts_before}")
        print(f"After: {counts_after}")
        print(f"Issues: {issues_after}")
        self.display()
        raise RuntimeError("Piece duplication detected in make_move")
    
    return result

def undo_move_with_validation(self):
    """Undo move with piece count validation"""
    
    # Count pieces before
    issues_before, counts_before = validate_piece_counts(self.board)
    
    # Call original undo_move
    original_undo_move(self)
    
    # Count pieces after
    issues_after, counts_after = validate_piece_counts(self.board)
    
    if issues_after:
        print(f"CORRUPTION DETECTED in undo_move!")
        print(f"Player: {self.p_move}")
        print(f"Before: {counts_before}")
        print(f"After: {counts_after}")
        print(f"Issues: {issues_after}")
        self.display()
        raise RuntimeError("Piece duplication detected in undo_move")

# Apply the monkey patches
ChessTable.make_move = make_move_with_validation
ChessTable.undo_move = undo_move_with_validation

def test_minimax_corruption():
    """Test minimax to catch corruption"""
    game = ChessTable()
    
    # Recreate the exact position from the failing game
    moves = [
        "d2d4", "b8c6", "a2a4", "g8f6", "e1d2", "c6d4", "a1a2", "f6e4"
    ]
    
    for move_str in moves:
        fx, fy = game.x.index(move_str[0]), game.y.index(move_str[1])
        tx, ty = game.x.index(move_str[2]), game.y.index(move_str[3])
        move = ((fx, fy), (tx, ty), None)
        game.make_move(move)
    
    print("Starting position (Turn 8 - White to move):")
    game.display()
    
    issues, counts = validate_piece_counts(game.board)
    print(f"Piece counts: {counts}")
    if issues:
        print(f"Issues: {issues}")
    
    print("\nTesting minimax...")
    try:
        best_move = choose_best_move(game, depth=3, max_time=3.0)
        print(f"Minimax succeeded: {best_move}")
    except Exception as e:
        print(f"Minimax failed: {e}")

if __name__ == "__main__":
    test_minimax_corruption()