# @title ChessTable

import math
import random
from copy import deepcopy
from pieces import Pawn, Knight, Bishop, Rook, Queen, King

class ChessTable:
    def __init__(self, state='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'):
        self.x = ['a','b','c','d','e','f','g','h']
        self.y = ['8','7','6','5','4','3','2','1']
        self.notation = {'p':1,'n':2,'b':3,'r':4,'q':5,'k':6}
        self.parts = {1:'Pawn',2:'Knight',3:'Bishop',4:'Rook',5:'Queen',6:'King'}
        self.weights = {1:1, # Pawn: 1
                        2:3, # Knight: 3
                        3:3, # Bishop: 3
                        4:6, # Rook: 5
                        5:9, # Queen: 9
                        6:1000} # King: 1000
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
        piece_map = {0: '.', 1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K'}
        state = ""
        for row in self.board:
            for piece in row:
                if piece == 0:
                    state += '.'
                else:
                    ch = piece_map[abs(piece)]
                    if piece < 0:
                        ch = ch.lower()
                    state += ch
        state += str(self.p_move)
        return state

    def register_position(self):
        # Registra a posição atual no contador de repetições
        state_str = self.get_state()
        self.position_counter[state_str] = self.position_counter.get(state_str, 0) + 1

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

        captured_white = [info['captured'] for info in self.log if info['captured'] > 0]
        captured_black = [info['captured'] for info in self.log if info['captured'] < 0]

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
      # Gera todos os movimentos que respeitam colisão/captura
      moves = []
      for y in range(8):
          for x in range(8):
              p = self.board[y][x]
              if p == 0:
                  continue
              if (p > 0 and player == 1) or (p < 0 and player == -1):
                  piece_type = abs(int(p))
                  cls_name = self.parts[piece_type]
                  piece_cls = globals()[cls_name]
                  poss = piece_cls.movement(self, player, (x, y), capture=True)
                  for dest in poss:
                      promotion = None
                      # Promoção
                      if piece_type == 1:
                          if (player == 1 and dest[1] == 0) or (player == -1 and dest[1] == 7):
                              for promo in ['q','r','b','n']:
                                  moves.append(((x,y), dest, promo))
                              continue
                      moves.append(((x,y), dest, None))
      return moves

    def is_square_attacked(self, square, by_player):
      # Varre todas as peças de by_player e verifica se alguma tem destino == square
      for y in range(8):
          for x in range(8):
              p = self.board[y][x]
              if p == 0:
                  continue
              if (p > 0 and by_player == 1) or (p < 0 and by_player == -1):
                  piece_type = abs(int(p))
                  cls_name = self.parts[piece_type]
                  piece_cls = globals()[cls_name]
                  poss = piece_cls.movement(self, by_player, (x, y), capture=True)
                  for dest in poss:
                      #print("destinos do adversario: ", poss)
                      if dest == square:
                          return True
      return False

    def find_king(self, player):
      target = 6  # King id
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

    def make_move(self, move):
      (fx,fy), (tx,ty), promotion = move
      moved = self.board[fy][fx]
      captured = self.board[ty][tx]
      info = {
          'move': move,
          'moved': moved,
          'captured': captured,
          'prev_en_passant': deepcopy(self.en_passant),
          'prev_castling': deepcopy(self.castling),
          'prev_p_move': self.p_move,
          'prev_halfmove_clock': self.halfmove_clock,
      }

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

      # Castling
      if abs(int(moved)) == 6 and abs(tx - fx) == 2:
          # Kingside
          if tx - fx == 2:
              rook_x = 7
              rook_to = tx - 1
          # Queenside
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

      # Desabilitar en passant
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
      # guardar no log
      self.log.append(info)
      self.history.append(deepcopy(self))
      return info

    def undo_move(self):
      # Desfazer movimento
      if not self.log:
          return
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
      if abs(int(moved)) == 1 and info['captured'] != 0 and (tx,ty) == info['move'][1] and info['prev_en_passant'] is not None:
          if info['captured'] != 0 and self.board[ty][tx] == 0:
              cap_y = ty + (1 if moved > 0 else -1)
              self.board[cap_y][tx] = info['captured']
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
      # Remove o último estado do tabuleiro do histórico
      if self.history:
        self.history.pop()

    def generate_legal_moves(self, player):
        # Geração de movimentos que não deixam o rei em cheque
        legal = []
        for move in self.generate_pseudo_legal_moves(player):
            self.make_move(move)          # Aplica temporariamente o movimento
            if not self.is_in_check(player):  # Verifica cheque do próprio jogador
                legal.append(move)        # Movimento permitido
            self.undo_move()              # Desfaz o movimento
        return legal


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
        return self.weights[piece_id]

    def evaluate(self):
        score = 0
        for y in range(8):
            for x in range(8):
                p = self.board[y][x]
                if p != 0:
                    piece_id = abs(int(p))
                    sign = 1 if p > 0 else -1
                    score += self.piece_score(piece_id, y, x) * sign
        # penalidade por repetição de posição
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