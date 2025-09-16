# @title ChessTable

import math
import random
from pieces import Pawn, Knight, Bishop, Rook, Queen, King

class ChessTable:
    def __init__(self, state='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'):
        self.x = ['a','b','c','d','e','f','g','h']
        self.y = ['8','7','6','5','4','3','2','1']
        self.notation = {'p':1,'n':2,'b':3,'r':4,'q':5,'k':6}
        self.parts = {1:'Pawn',2:'Knight',3:'Bishop',4:'Rook',5:'Queen',6:'King'}
        self.weights = {1:1, # Peão: 1
                        2:3, # Cavalo: 3
                        3:3, # Bispo: 3
                        4:6, # Torre: 5
                        5:9, # Rainha: 9
                        6:1000} # Rei: 1000
        self.reset(state=state)

    def reset(self, state):
        self.history = []
        self.log = []
        self.init_pos = state
        self.state_table = {}
        self.p_move = 1
        self.castling = [1, 1, 1, 1]
        self.en_passant = None
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.position_counter = {}
        self.halfmove_clock = 0
        self.load_state(state)
        self.register_position()

    def board_2_array(self, coord):
        file = self.x.index(coord[0])
        rank = self.y.index(coord[1])
        return (file, rank)

    def load_state(self,state):
        data = state.split(' ')
        if len(data) == 4:
            for y,rank in enumerate(data[0].split('/')):
                x = 0
                for p in rank:
                    if p.isdigit():
                        for _ in range(int(p)):
                            self.board[y][x] = 0
                            x += 1
                    else:
                        self.board[y][x] = self.notation[p.lower()] * (-1 if p.islower() else 1)
                        x += 1
            self.p_move = 1 if data[1] == 'w' else -1
            self.castling = [
                1 if 'K' in data[2] else 0,
                1 if 'Q' in data[2] else 0,
                1 if 'k' in data[2] else 0,
                1 if 'q' in data[2] else 0,
            ]
            self.en_passant = None if data[3] == '-' else self.board_2_array(data[3])
            return True
        return False

    def get_state(self):
        # Optimized state generation using list comprehension and join
        piece_map = {0: '.', 1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K'}
        state_chars = []
        for row in self.board:
            for piece in row:
                if piece == 0:
                    state_chars.append('.')
                else:
                    ch = piece_map[abs(piece)]
                    state_chars.append(ch.lower() if piece < 0 else ch)
        state_chars.append(str(self.p_move))
        return ''.join(state_chars)
    
    def get_state_hash(self):
        # Fast hash-based state representation for transposition table
        # Using tuple of tuples for board state (hashable and fast)
        board_tuple = tuple(tuple(row) for row in self.board)
        return hash((board_tuple, self.p_move, tuple(self.castling), self.en_passant))

    def register_position(self):
        # Registra a posição atual no contador de repetições
        state_str = self.get_state()
        self.position_counter[state_str] = self.position_counter.get(state_str, 0) + 1
        
        # Previne que position_counter cresça muito limpando entradas antigas
        if len(self.position_counter) > 100:
            # Mantém apenas entradas com count > 1 (repetições potenciais)
            self.position_counter = {k: v for k, v in self.position_counter.items() if v > 1}

    def unregister_position(self):
        # Remove a posição atual do contador ao desfazer
        state_str = self.get_state()
        if state_str in self.position_counter:
            self.position_counter[state_str] -= 1
            if self.position_counter[state_str] == 0:
                del self.position_counter[state_str]

    def display(self):
        weights = {1:'P',2:'N',3:'B',4:'R',5:'Q',6:'K'}
        print("   a b c d e f g h")
        print("   -----------------")
        for y in range(8):
            line = f"{8-y} |"
            for x in range(8):
                p = self.board[y][x]
                if p != 0:
                    ch = weights[abs(p)]
                    if p < 0:
                        ch = ch.lower()
                    line += ch + " "
                else:
                    line += ". "
            line += f"| {8-y}"
            print(line)
        print("   -----------------")
        print("   a b c d e f g h\n")

        captured_white = [info['captured'] for info in self.log if info['captured'] < 0]  # Black pieces captured by white
        captured_black = [info['captured'] for info in self.log if info['captured'] > 0]  # White pieces captured by black

        def pieces_to_string(p_list):
            s = ""
            for p in p_list:
                ch = weights[abs(p)]
                if p < 0:
                    ch = ch.lower()
                s += ch + " "
            return s

        print("Peças capturadas:")
        print("Brancas:", pieces_to_string(captured_white))
        print("Pretas:", pieces_to_string(captured_black))

    def square_to_algebraic(self, pos):
        return f"{self.x[pos[0]]}{self.y[pos[1]]}"

    def algebraic_to_square(self, s):
        file = s[0]
        rank = s[1]
        return (self.x.index(file), self.y.index(rank))

    def generate_pseudo_legal_moves(self, player):
      # Geração otimizada de movimentos pseudo-legais
      moves = []
      for y in range(8):
          for x in range(8):
              p = self.board[y][x]
              # Only consider pieces belonging to the current player
              if p == 0 or (p > 0 and player != 1) or (p < 0 and player != -1):
                  continue
              
              piece_type = abs(int(p))
              # Usa cálculo de movimento otimizado
              poss = self.get_piece_moves_fast(piece_type, player, (x, y))
              
              for dest in poss:
                  # Skip if trying to move to a square occupied by own piece
                  dest_piece = self.board[dest[1]][dest[0]]
                  if dest_piece != 0 and ((dest_piece > 0 and player == 1) or (dest_piece < 0 and player == -1)):
                      continue
                  
                  # Promoção
                  if piece_type == 1:
                      if (player == 1 and dest[1] == 0) or (player == -1 and dest[1] == 7):
                          for promo in ['q','r','b','n']:
                              moves.append(((x,y), dest, promo))
                          continue
                  moves.append(((x,y), dest, None))
      return moves
    
    def get_piece_moves_fast(self, piece_type, player, pos):
        """
        Cálculo de movimento de peça mais rápido sem instanciação de classe
        """
        x, y = pos
        moves = []
        
        if piece_type == 1:  # Peão
            direction = -1 if player == 1 else 1
            start_row = 6 if player == 1 else 1
            
            # Movimento para frente
            one_step_y = y + direction
            if 0 <= one_step_y <= 7 and self.board[one_step_y][x] == 0:
                moves.append((x, one_step_y))
                # Movimento duplo da posição inicial
                if y == start_row and self.board[y + 2 * direction][x] == 0:
                    moves.append((x, y + 2 * direction))
            
            # Capturas
            for dx in [-1, 1]:
                nx, ny = x + dx, y + direction
                if 0 <= nx <= 7 and 0 <= ny <= 7:
                    cell = self.board[ny][nx]
                    if cell * player < 0 or (self.en_passant == (nx, ny) and cell == 0):
                        moves.append((nx, ny))
                        
        elif piece_type == 2:  # Cavalo
            knight_moves = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
            for dx, dy in knight_moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx <= 7 and 0 <= ny <= 7:
                    cell = self.board[ny][nx]
                    if cell == 0 or cell * player < 0:
                        moves.append((nx, ny))
                        
        elif piece_type == 3:  # Bispo
            for dx, dy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                moves.extend(self.get_sliding_moves(pos, dx, dy, player))
                
        elif piece_type == 4:  # Torre
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                moves.extend(self.get_sliding_moves(pos, dx, dy, player))
                
        elif piece_type == 5:  # Rainha
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                moves.extend(self.get_sliding_moves(pos, dx, dy, player))
                
        elif piece_type == 6:  # Rei
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx <= 7 and 0 <= ny <= 7:
                        cell = self.board[ny][nx]
                        if cell == 0 or cell * player < 0:
                            moves.append((nx, ny))
            
            # Roque - only if king is on starting position
            king_start_y = 7 if player == 1 else 0
            if pos == (4, king_start_y) and not self.is_in_check(player):
                # Roque pequeno (kingside)
                if (self.board[king_start_y][5] == 0 and self.board[king_start_y][6] == 0 and
                    self.board[king_start_y][7] == player * 4):  # Rook in place
                    if (self.castling[0] == 1 and player == 1) or (self.castling[2] == 1 and player == -1):
                        # Check if squares king moves through are not attacked
                        if (not self.is_square_attacked((5, king_start_y), -player) and
                            not self.is_square_attacked((6, king_start_y), -player)):
                            moves.append((6, king_start_y))
                # Roque grande (queenside)
                if (self.board[king_start_y][3] == 0 and self.board[king_start_y][2] == 0 and
                    self.board[king_start_y][1] == 0 and self.board[king_start_y][0] == player * 4):  # Rook in place
                    if (self.castling[1] == 1 and player == 1) or (self.castling[3] == 1 and player == -1):
                        # Check if squares king moves through are not attacked
                        if (not self.is_square_attacked((3, king_start_y), -player) and
                            not self.is_square_attacked((2, king_start_y), -player)):
                            moves.append((2, king_start_y))
        
        return moves
    
    def get_sliding_moves(self, pos, dx, dy, player):
        """
        Obtém movimentos para peças deslizantes (torre, bispo, rainha)
        """
        moves = []
        x, y = pos
        for step in range(1, 8):
            nx, ny = x + dx * step, y + dy * step
            if not (0 <= nx <= 7 and 0 <= ny <= 7):
                break
            cell = self.board[ny][nx]
            if cell == 0:
                moves.append((nx, ny))
            elif cell * player < 0:
                moves.append((nx, ny))
                break
            else:
                break
        return moves

    def get_piece_moves_for_attack_check(self, piece_type, player, pos):
        """
        Simplified move generation for attack detection - does NOT check castling to avoid recursion
        """
        x, y = pos
        moves = []
        
        if piece_type == 1:  # Peão
            direction = -1 if player == 1 else 1
            start_row = 6 if player == 1 else 1
            
            # Movimento para frente
            one_step_y = y + direction
            if 0 <= one_step_y <= 7 and self.board[one_step_y][x] == 0:
                moves.append((x, one_step_y))
                # Movimento duplo da posição inicial
                if y == start_row and self.board[y + 2 * direction][x] == 0:
                    moves.append((x, y + 2 * direction))
            
            # Capturas
            for dx in [-1, 1]:
                nx, ny = x + dx, y + direction
                if 0 <= nx <= 7 and 0 <= ny <= 7:
                    cell = self.board[ny][nx]
                    if cell * player < 0 or (self.en_passant == (nx, ny) and cell == 0):
                        moves.append((nx, ny))
                        
        elif piece_type == 2:  # Cavalo
            knight_moves = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
            for dx, dy in knight_moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx <= 7 and 0 <= ny <= 7:
                    cell = self.board[ny][nx]
                    if cell == 0 or cell * player < 0:
                        moves.append((nx, ny))
                        
        elif piece_type == 3:  # Bispo
            for dx, dy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                moves.extend(self.get_sliding_moves(pos, dx, dy, player))
                
        elif piece_type == 4:  # Torre
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                moves.extend(self.get_sliding_moves(pos, dx, dy, player))
                
        elif piece_type == 5:  # Rainha
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]:
                moves.extend(self.get_sliding_moves(pos, dx, dy, player))
                
        elif piece_type == 6:  # Rei - NO CASTLING CHECK to avoid recursion
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx <= 7 and 0 <= ny <= 7:
                        cell = self.board[ny][nx]
                        if cell == 0 or cell * player < 0:
                            moves.append((nx, ny))
        
        return moves
    
    def is_square_attacked(self, square, by_player):
      # Varre todas as peças de by_player e verifica se alguma tem destino == square
      for y in range(8):
          for x in range(8):
              p = self.board[y][x]
              if p == 0:
                  continue
              # Check if piece belongs to the attacking player
              if (p > 0 and by_player == 1) or (p < 0 and by_player == -1):
                  piece_type = abs(int(p))
                  # Use the simplified move generation that doesn't check castling
                  poss = self.get_piece_moves_for_attack_check(piece_type, by_player, (x, y))
                  for dest in poss:
                      if dest == square:
                          return True
      return False

    def find_king(self, player):
      target = 6  # ID do Rei
      for y in range(8):
          for x in range(8):
              if self.board[y][x] == target * player:
                  return (x, y)
      return None

    def is_in_check(self, player):
      king_pos = self.find_king(player)
      if not king_pos:
          return True
      result = self.is_square_attacked(king_pos, -player)
      return result

    def _validate_piece_counts(self, operation="unknown"):
        """Check for impossible piece counts to catch duplication bugs"""
        piece_count = {}
        for y in range(8):
            for x in range(8):
                piece = self.board[y][x]
                if piece != 0:
                    piece_count[piece] = piece_count.get(piece, 0) + 1
        
        # Check for impossible piece counts (basic validation)
        white_pawns = piece_count.get(1, 0)
        black_pawns = piece_count.get(-1, 0)
        if white_pawns > 8:
            raise RuntimeError(f"CORRUPTION DETECTED: Too many white pawns: {white_pawns} during {operation}")
        if black_pawns > 8:
            raise RuntimeError(f"CORRUPTION DETECTED: Too many black pawns: {black_pawns} during {operation}")
    
    def make_move(self, move):
      (fx,fy), (tx,ty), promotion = move
      
      # Basic validation to prevent completely invalid moves
      if not (0 <= fx <= 7 and 0 <= fy <= 7 and 0 <= tx <= 7 and 0 <= ty <= 7):
          raise ValueError(f"Invalid move coordinates: {move}")
          
      moved = self.board[fy][fx]
      captured = self.board[ty][tx]
      
      # Can't move empty square
      if moved == 0:
          raise ValueError(f"No piece at source square {(fx, fy)}")
          
      # Can't move opponent's piece
      if (moved > 0 and self.p_move != 1) or (moved < 0 and self.p_move != -1):
          raise ValueError(f"Cannot move opponent's piece: {moved} when player is {self.p_move}")
          
      # Can't capture own piece
      if captured != 0 and ((captured > 0 and self.p_move == 1) or (captured < 0 and self.p_move == -1)):
          raise ValueError(f"Cannot capture own piece: {captured}")
      info = {
          'move': move,
          'moved': moved,
          'captured': captured,
          'prev_en_passant': self.en_passant,  # Simple assignment is fine
          'prev_castling': self.castling[:],   # Shallow copy is sufficient and much faster
          'prev_p_move': self.p_move,
          'prev_halfmove_clock': self.halfmove_clock,
      }
      
      # Use separate log for search moves vs actual game moves
      if not hasattr(self, 'search_log'):
          self.search_log = []

      # Atualiza o contador de lances
      if abs(int(moved)) == 1 or captured != 0:
          self.halfmove_clock = 0 # Reseta o contador se for um movimento de peão ou uma captura
      else:
          self.halfmove_clock += 1 # Incrementa o contador para outras jogadas

      # En passant
      if abs(int(moved)) == 1 and (tx,ty) == self.en_passant and captured == 0:
          cap_y = ty + (1 if moved > 0 else -1)
          info['captured'] = self.board[cap_y][tx]
          self.board[cap_y][tx] = 0

      # Mover peça
      self.board[fy][fx] = 0
      self.board[ty][tx] = moved

      # Promoção
      if abs(int(moved)) == 1 and promotion is not None:
          promo_map = {'q':5,'r':4,'b':3,'n':2}
          val = promo_map[promotion]
          self.board[ty][tx] = val * (1 if moved > 0 else -1)

      # Roque
      if abs(int(moved)) == 6 and abs(tx - fx) == 2:
          # Roque pequeno
          if tx - fx == 2:
              rook_x = 7
              rook_to = tx - 1
          # Roque grande
          else:
              rook_x = 0
              rook_to = tx + 1
          rook_y = fy
          rook_piece = self.board[rook_y][rook_x]
          self.board[rook_y][rook_x] = 0
          self.board[rook_y][rook_to] = rook_piece

      # Atualizar en passant
      self.en_passant = None
      if abs(int(moved)) == 1 and abs(ty - fy) == 2:
          mid_y = (fy + ty) // 2
          self.en_passant = (tx, mid_y)

      # Desabilitar roque
      if moved == 6:
          self.castling[0] = 0
          self.castling[1] = 0
      if moved == -6:
          self.castling[2] = 0
          self.castling[3] = 0
      # torres
      if (fx,fy) == (0,7) or (tx,ty) == (0,7):
          self.castling[1] = 0
      if (fx,fy) == (7,7) or (tx,ty) == (7,7):
          self.castling[0] = 0
      if (fx,fy) == (0,0) or (tx,ty) == (0,0):
          self.castling[3] = 0
      if (fx,fy) == (7,0) or (tx,ty) == (7,0):
          self.castling[2] = 0

      # alterna jogador
      self.p_move *= -1
      
      # Validate piece counts after move
      self._validate_piece_counts(f"make_move {move}")
      
      # Use different logs for search vs actual game moves
      if hasattr(self, '_in_search') and self._in_search:
          # During search - use temporary search log
          if not hasattr(self, 'search_log'):
              self.search_log = []
          self.search_log.append(info)
          # Debug: track search depth
          if not hasattr(self, '_search_depth'):
              self._search_depth = 0
          self._search_depth += 1
      else:
          # During actual gameplay - use main log
          self.log.append(info)
          # Register the new position for repetition detection
          self.register_position()
      
      return info

    def undo_move(self):
      # Desfazer movimento - use correct log based on search state
      if hasattr(self, '_in_search') and self._in_search:
          # During search - use search log
          if not hasattr(self, 'search_log') or not self.search_log:
              print(f"WARNING: Trying to undo search move but search log is empty!")
              return
          info = self.search_log.pop()
          # Debug: track search depth
          if hasattr(self, '_search_depth'):
              self._search_depth -= 1
      else:
          # During actual gameplay - use main log  
          if not self.log:
              return
          # Unregister the current position before undoing
          self.unregister_position()
          info = self.log.pop()
      (fx,fy), (tx,ty), promotion = info['move']
      self.p_move = info['prev_p_move']
      self.en_passant = info['prev_en_passant']
      self.castling = info['prev_castling']
      self.halfmove_clock = info['prev_halfmove_clock']

      moved = info['moved']
      self.board[fy][fx] = moved
      self.board[ty][tx] = info['captured']

      # Restaura en passant
      # An en passant capture was made if:
      # 1. A pawn moved to the en passant square
      # 2. No piece was captured on the destination square (info['captured'] should be 0 for normal en passant)
      # 3. There was an en passant target set when the move was made
      if (abs(int(moved)) == 1 and 
          info['prev_en_passant'] is not None and 
          (tx, ty) == info['prev_en_passant']):
          
          # This was an en passant capture
          # The captured pawn was stored separately during make_move
          # We need to restore it to the square beside the en passant target
          cap_y = ty + (1 if moved > 0 else -1)
          # The captured piece was stored in info when make_move detected en passant
          if 'captured' in info and info['captured'] != 0:
              self.board[cap_y][tx] = info['captured']
              # Clear the destination square since no piece was actually there
              self.board[ty][tx] = 0

      # Restaura roque
      if abs(int(moved)) == 6 and abs(tx - fx) == 2:
          if tx - fx == 2:
              rook_from = (tx - 1, ty)
              rook_to = (7, ty)
          else:
              rook_from = (tx + 1, ty)
              rook_to = (0, ty)
          rook_piece = self.board[rook_from[1]][rook_from[0]]
          self.board[rook_from[1]][rook_from[0]] = 0
          self.board[rook_to[1]][rook_to[0]] = rook_piece
      
      # Validate piece counts after undo
      self._validate_piece_counts("undo_move")
      
      # Remove o último estado do tabuleiro do histórico
      if self.history:
        self.history.pop()

    def generate_legal_moves(self, player):
        # Geração de movimentos legais mais rápida usando detecção leve de xeque
        legal = []
        king_pos = self.find_king(player)
        if not king_pos:
            return legal
            
        for move in self.generate_pseudo_legal_moves(player):
            if self.is_move_legal_fast(move, player, king_pos):
                legal.append(move)
        return legal
    
    def is_move_legal_fast(self, move, player, king_pos):
        """
        Validação rápida de movimento legal sem make_move/undo_move completo
        """
        (fx, fy), (tx, ty), promotion = move
        
        # Basic validation first
        if not (0 <= fx <= 7 and 0 <= fy <= 7 and 0 <= tx <= 7 and 0 <= ty <= 7):
            return False
            
        moved_piece = self.board[fy][fx]
        captured_piece = self.board[ty][tx]
        
        # Can't move empty square or opponent's piece
        if moved_piece == 0 or (moved_piece > 0 and player != 1) or (moved_piece < 0 and player != -1):
            return False
            
        # Can't capture own piece
        if captured_piece != 0 and ((captured_piece > 0 and player == 1) or (captured_piece < 0 and player == -1)):
            return False
        
        # Special castling validation
        if abs(moved_piece) == 6 and abs(tx - fx) == 2:
            # This is castling, validate it properly
            king_start_y = 7 if player == 1 else 0
            if fy != king_start_y or fx != 4:
                return False
            if self.is_in_check(player):
                return False
            # Check castling rights and path
            if tx == 6:  # Kingside
                if not ((self.castling[0] == 1 and player == 1) or (self.castling[2] == 1 and player == -1)):
                    return False
                if self.board[fy][5] != 0 or self.board[fy][6] != 0:
                    return False
            elif tx == 2:  # Queenside
                if not ((self.castling[1] == 1 and player == 1) or (self.castling[3] == 1 and player == -1)):
                    return False
                if self.board[fy][1] != 0 or self.board[fy][2] != 0 or self.board[fy][3] != 0:
                    return False
        
        # Temporariamente faz o movimento apenas no tabuleiro
        self.board[fy][fx] = 0
        self.board[ty][tx] = moved_piece
        
        # Atualiza posição do rei se o rei se moveu
        new_king_pos = king_pos
        if abs(moved_piece) == 6:  # Rei se moveu
            new_king_pos = (tx, ty)
        
        # Verifica se o rei estaria em xeque
        is_legal = not self.is_square_attacked_fast(new_king_pos, -player)
        
        # Restaura o tabuleiro
        self.board[fy][fx] = moved_piece
        self.board[ty][tx] = captured_piece
        
        return is_legal
    
    def is_square_attacked_fast(self, square, by_player):
        """
        Versão mais rápida de is_square_attacked com otimizações
        """
        sx, sy = square
        
        # Verifica ataques de peão (mais comuns)
        pawn_dir = 1 if by_player == 1 else -1
        for dx in [-1, 1]:
            px, py = sx + dx, sy + pawn_dir
            if 0 <= px <= 7 and 0 <= py <= 7:
                piece = self.board[py][px]
                if piece == by_player * 1:  # Peão
                    return True
        
        # Verifica ataques do rei (1 casa em todas as direções)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                kx, ky = sx + dx, sy + dy
                if 0 <= kx <= 7 and 0 <= ky <= 7:
                    piece = self.board[ky][kx]
                    if piece == by_player * 6:  # Rei
                        return True
        
        # Verifica ataques do cavalo
        knight_moves = [(2,1), (2,-1), (-2,1), (-2,-1), (1,2), (1,-2), (-1,2), (-1,-2)]
        for dx, dy in knight_moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx <= 7 and 0 <= ny <= 7:
                piece = self.board[ny][nx]
                if piece == by_player * 2:  # Cavalo
                    return True
        
        # Verifica ataques de peças deslizantes (torre, bispo, rainha)
        # Horizontal e vertical (torre e rainha)
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            for step in range(1, 8):
                rx, ry = sx + dx * step, sy + dy * step
                if not (0 <= rx <= 7 and 0 <= ry <= 7):
                    break
                piece = self.board[ry][rx]
                if piece != 0:
                    if piece == by_player * 4 or piece == by_player * 5:  # Torre ou Rainha
                        return True
                    break
        
        # Diagonal (bispo e rainha)
        for dx, dy in [(1,1), (1,-1), (-1,1), (-1,-1)]:
            for step in range(1, 8):
                bx, by = sx + dx * step, sy + dy * step
                if not (0 <= bx <= 7 and 0 <= by <= 7):
                    break
                piece = self.board[by][bx]
                if piece != 0:
                    if piece == by_player * 3 or piece == by_player * 5:  # Bispo ou Rainha
                        return True
                    break
        
        return False


    def choose_move(self, depth=3):
        # Seleção do melhor movimento disponível
        score, move = self.minimax_ab(depth, -math.inf, math.inf, self.p_move)
        return move

    def choose_random_move(self):
        # Seleção de um movimento aleatório disponível
        legal_moves = self.generate_legal_moves(self.p_move)
        if legal_moves:
          return random.choice(legal_moves)
        return None

    def piece_score(self, piece_id, y, x):
        base_score = self.weights[piece_id]
        
        # Add positional bonuses for better play
        positional_bonus = 0
        
        if piece_id == 1:  # Pawn
            # Encourage pawn advancement
            if y < 4:  # White pawn advanced
                positional_bonus += (6 - y) * 0.1
            elif y > 3:  # Black pawn advanced 
                positional_bonus += (y - 1) * 0.1
            # Center pawns are more valuable
            if x in [3, 4]:
                positional_bonus += 0.2
                
        elif piece_id == 2:  # Knight
            # Knights are better in the center
            center_distance = abs(x - 3.5) + abs(y - 3.5)
            positional_bonus += (7 - center_distance) * 0.1
            
        elif piece_id == 3:  # Bishop
            # Bishops prefer long diagonals
            if (x + y) % 2 == 0:  # Light squared bishop
                positional_bonus += 0.1
            else:  # Dark squared bishop
                positional_bonus += 0.1
                
        elif piece_id == 4:  # Rook
            # Rooks prefer open files and back rank
            if y in [0, 7]:  # Back rank
                positional_bonus += 0.3
                
        elif piece_id == 6:  # King
            # King safety - prefer corners/edges in opening/middlegame
            if y in [0, 7] and x in range(1, 7):  # Castled position
                positional_bonus += 0.5
        
        return base_score + positional_bonus

    def evaluate(self):
        score = 0
        for y in range(8):
            for x in range(8):
                p = self.board[y][x]
                if p != 0:
                    piece_id = abs(int(p))
                    sign = 1 if p > 0 else -1
                    score += self.piece_score(piece_id, y, x) * sign
        
        # Verifica repetições apenas se temos histórico suficiente (otimização)
        if len(self.position_counter) > 1:
            state_str = self.get_state()
            repetitions = self.position_counter.get(state_str, 0)
            if repetitions > 1:
                score -= repetitions * 50
        return score * self.p_move

    def uci_to_move(self, uci_move):
        # UCI (ex: 'e2e4', 'e7e8q') para tupla ((fx,fy),(tx,ty), promotion)
        if len(uci_move) < 4:
            return None

        from_str = uci_move[0:2]
        to_str = uci_move[2:4]

        try:
            from_pos = self.algebraic_to_square(from_str)
            to_pos = self.algebraic_to_square(to_str)
        except ValueError:
            return None  # Retorna None para entradas inválidas

        promotion = None
        if len(uci_move) == 5:
            promo_char = uci_move[4].lower()
            if promo_char in ['q', 'r', 'b', 'n']:
                promotion = promo_char
            else:
                return None # Caractere de promoção inválido
        return (from_pos, to_pos, promotion)

    def move_to_uci(self, move):
      # Tupla ((fx,fy),(tx,ty), promotion) para UCI (ex: 'e2e4', 'e7e8q')
      (from_pos, to_pos, promotion) = move
      uci = self.square_to_algebraic(from_pos) + self.square_to_algebraic(to_pos)
      if promotion:
          uci += promotion
      return uci