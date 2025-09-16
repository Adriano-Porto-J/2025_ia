#!/usr/bin/env python3

from chessTable import ChessTable

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
    
    # Pawns: max 8 per side
    white_pawns = counts.get(1, 0)
    black_pawns = counts.get(-1, 0)
    if white_pawns > 8:
        issues.append(f"Too many white pawns: {white_pawns}")
    if black_pawns > 8:
        issues.append(f"Too many black pawns: {black_pawns}")
    
    # Knights: max 10 per side (8 from promotion + 2 original)
    white_knights = counts.get(2, 0)
    black_knights = counts.get(-2, 0)
    if white_knights > 10:
        issues.append(f"Too many white knights: {white_knights}")
    if black_knights > 10:
        issues.append(f"Too many black knights: {black_knights}")
    
    # Kings: exactly 1 per side
    white_kings = counts.get(6, 0)
    black_kings = counts.get(-6, 0)
    if white_kings != 1:
        issues.append(f"Wrong number of white kings: {white_kings}")
    if black_kings != 1:
        issues.append(f"Wrong number of black kings: {black_kings}")
    
    return issues, counts

def debug_make_undo():
    """Test make_move and undo_move for piece duplication"""
    game = ChessTable()
    game._in_search = True
    
    print("=== TESTING MAKE/UNDO FOR PIECE DUPLICATION ===")
    
    # Test some moves
    legal_moves = game.generate_legal_moves(game.p_move)[:5]
    
    for i, move in enumerate(legal_moves):
        print(f"\n--- Testing move {i}: {move} ---")
        
        # Count pieces before
        issues_before, counts_before = validate_piece_counts(game.board)
        print(f"Before: {counts_before}")
        if issues_before:
            print(f"Issues before: {issues_before}")
        
        # Make move
        try:
            info = game.make_move(move)
            print(f"Move made successfully")
            
            # Count pieces after make_move
            issues_after_make, counts_after_make = validate_piece_counts(game.board)
            print(f"After make: {counts_after_make}")
            if issues_after_make:
                print(f"Issues after make: {issues_after_make}")
            
            # Undo move
            game.undo_move()
            print(f"Move undone successfully")
            
            # Count pieces after undo
            issues_after_undo, counts_after_undo = validate_piece_counts(game.board)
            print(f"After undo: {counts_after_undo}")
            if issues_after_undo:
                print(f"Issues after undo: {issues_after_undo}")
            
            # Check if we're back to the original state
            if counts_before != counts_after_undo:
                print(f"ERROR: Piece counts not restored! Before: {counts_before}, After: {counts_after_undo}")
                return
            
        except Exception as e:
            print(f"Error during move: {e}")
            return
    
    print("\n=== NESTED MAKE/UNDO TEST ===")
    # Test nested make/undo (like in minimax)
    
    move1 = legal_moves[0]
    move2 = legal_moves[1]
    
    print(f"Testing nested moves: {move1}, {move2}")
    
    # Original state
    issues_orig, counts_orig = validate_piece_counts(game.board)
    print(f"Original: {counts_orig}")
    
    # Make first move
    game.make_move(move1)
    issues_1, counts_1 = validate_piece_counts(game.board)
    print(f"After move 1: {counts_1}")
    if issues_1:
        print(f"Issues after move 1: {issues_1}")
    
    # Make second move
    legal_moves_2 = game.generate_legal_moves(game.p_move)
    if legal_moves_2:
        move2_actual = legal_moves_2[0]
        game.make_move(move2_actual)
        issues_2, counts_2 = validate_piece_counts(game.board)
        print(f"After move 2: {counts_2}")
        if issues_2:
            print(f"Issues after move 2: {issues_2}")
        
        # Undo second move
        game.undo_move()
        issues_after_undo2, counts_after_undo2 = validate_piece_counts(game.board)
        print(f"After undo 2: {counts_after_undo2}")
        if issues_after_undo2:
            print(f"Issues after undo 2: {issues_after_undo2}")
        
        if counts_1 != counts_after_undo2:
            print(f"ERROR: Second undo failed! Expected: {counts_1}, Got: {counts_after_undo2}")
    
    # Undo first move
    game.undo_move()
    issues_final, counts_final = validate_piece_counts(game.board)
    print(f"Final: {counts_final}")
    if issues_final:
        print(f"Issues final: {issues_final}")
    
    if counts_orig != counts_final:
        print(f"ERROR: First undo failed! Expected: {counts_orig}, Got: {counts_final}")
    else:
        print("SUCCESS: All moves undone correctly!")

if __name__ == "__main__":
    debug_make_undo()