
def move(game, player, pos, dx, dy, amt, capture=True):
    """
    Calcula os movimentos possíveis em uma linha reta (horizontal, vertical ou diagonal) a partir de uma posição

    Args:
        game: tabuleiro
        player: O jogador atual (1 para branco, -1 para preto)
        pos: A posição da peça (x, y)
        dx: A direção horizontal (1, 0, -1)
        dy: A direção vertical (1, 0, -1)
        amt: A quantidade de casas a serem percorridas
        capture: Se a peça pode capturar

    Returns:
        Uma lista de tuplas (x, y) com as posições válidas
    """
    result = []
    for step in range(1, amt+1):
        x = pos[0] + dx * step
        y = pos[1] + dy * step
        if 0 <= x <= 7 and 0 <= y <= 7:
            cell = game.board[y][x]
            if cell == 0:
                result.append((x, y))
            elif cell * player < 0 and capture:
                result.append((x, y))
                break
            else:
                break
        else:
            break
    return result

# @title Pawn
class Pawn:
  def __init__(self):
    self.value = 1  # Valor da peça peão
    self.notation = ''  # Notação da peça

  # Peão se move apenas para frente ou diagonal na hora da captura
  def movement(game, player, pos, capture=True):
    result = []  # Lista para as jogadas possíveis
    direction = -1 if player == 1 else 1  # -1 para branco, 1 para preto
    start_row = 6 if player == 1 else 1  # Linha inicial do peão

    x, y = pos

    # Movimento de 1 casa para frente (se estiver vazio)
    one_step_y = y + direction
    if 0 <= one_step_y <= 7 and game.board[one_step_y][x] == 0:
      result.append((x, one_step_y))

      # Movimento de 2 casas para frente (somente da posição inicial e se as 2 casas estiverem livres)
      two_step_y = y + 2 * direction
      if y == start_row and game.board[two_step_y][x] == 0:
        result.append((x, two_step_y))

    # Capturas diagonais
    if capture:
      for dx in [-1, 1]:
        target_x = x + dx
        target_y = y + direction

        if 0 <= target_x <= 7 and 0 <= target_y <= 7:
          cell = game.board[target_y][target_x]

          # Captura normal
          if cell * player < 0:
            result.append((target_x, target_y))

          # En Passant
          if game.en_passant == (target_x, target_y) and game.board[target_y][target_x] == 0:
            result.append((target_x, target_y))

    return result  # Retorna a lista com as jogadas possíveis
# @title Knight
class Knight:
    def __init__(self):
        self.value = 2 # Valor da peça cavalo
        self.notation = 'N' # Notação da peça

    # Cavalo se move apenas em "L"
    def movement(game, player, pos, capture=True):
        result = [] # Lista com as jogadas possíveis do cavalo
        moves = [
          (pos[0] + 1, pos[1] + 2), (pos[0] + 1, pos[1] - 2),
          (pos[0] - 1, pos[1] + 2), (pos[0] - 1, pos[1] - 2),
          (pos[0] + 2, pos[1] + 1), (pos[0] + 2, pos[1] - 1),
          (pos[0] - 2, pos[1] + 1), (pos[0] - 2, pos[1] - 1)
        ] # Movimentações possíveis do cavalo

        # Verifica se a posição está dentro do tabuleiro
        # Adiciona a posição se estiver vazia ou se houver peça inimiga
        for x, y in moves:
            if 0 <= x <= 7 and 0 <= y <= 7:
                cell = game.board[y][x]
                if cell == 0 or cell * player < 0:
                    result.append((x, y))

        return result # Retorna a lista com as jogadas possiveis

# @title Bishop
class Bishop:
    def __init__(self):
        self.value = 3 # Valor da peça Bispo
        self.notation = 'B' #Notação da peça Bispo

    #Bispo se movimenta apenas na diagonal
    def movement(game, player, pos, capture=True):
        result = []

        result += move(game, player, pos, 1, 1, 7, capture) # Diagonal nordeste
        result += move(game, player, pos, 1, -1, 7, capture) # Diagonal sudeste
        result += move(game, player, pos, -1, 1, 7, capture) # Diagonal noroeste
        result += move(game, player, pos, -1, -1, 7, capture) # Diagonal sudoeste

        return result # Retorna a lista com as jogadas possíveis

# @title Rook
class Rook:
  def __init__(self):
      self.value = 4 # Valor peça torre
      self.notation = 'R' # Notação da peça torre

  # Torre se movimenta em retas perpendiculares a partir da sua posição
  def movement(game, player, pos, capture=True):
      result = [] # Lista com as possiveis jogadas da torre

      result += move(game, player, pos, 0, 1, 7, capture) # Movimento vertical para cima
      result += move(game, player, pos, 0, -1, 7, capture) # Movimento vertical para baixo
      result += move(game, player, pos, 1, 0, 7, capture) # Movimento horizontal para a direita
      result += move(game, player, pos, -1, 0, 7, capture) # Movimento horizontal para a esquerda

      return result # Retorna a lista com as ppossiveis jogadas
# @title Queen

class Queen:
  def __init__(self):
      self.value = 5 # Valor numerico da rainha
      self.notation = 'Q' # Notação da rainha

  def movement(game, player, pos, capture=True):
      result = [] # Lista de possiveis jogadas da rainha

      # Combina os movimentos de Torre e Bispo
      result += move(game, player, pos, 0, 1, 7, capture)  # Cima
      result += move(game, player, pos, 0, -1, 7, capture) # Baixo
      result += move(game, player, pos, 1, 0, 7, capture)  # Direita
      result += move(game, player, pos, -1, 0, 7, capture) # Esquerda
      result += move(game, player, pos, 1, 1, 7, capture)  # Diagonal Cima-Direita
      result += move(game, player, pos, 1, -1, 7, capture) # Diagonal Baixo-Direita
      result += move(game, player, pos, -1, 1, 7, capture) # Diagonal Cima-Esquerda
      result += move(game, player, pos, -1, -1, 7, capture)# Diagonal Baixo-Esquerda

      return result #retorna lista com as possívveis jogadas

# @title King

class King:
  def __init__(self):
      self.value = 6 # Valor numérico do rei
      self.notation = 'K' # Notação do rei

  def movement(game, player, pos, capture=True):
      result = []

      # Movimentos de 1 casa em todas as direções (vertical, horizontal e diagonal)
      directions = [
        (0, 1),  (0, -1),  # Vertical
        (1, 0),  (-1, 0),  # Horizontal
        (1, 1),  (1, -1),  # Diagonais
        (-1, 1), (-1, -1)
        ]

      for dx, dy in directions:
        result += move(game, player, pos, dx, dy, 1, capture)

      # Roque (Castling)
      # Rei na posição inicial (branco: (4,7), preto: (4,0))
      if pos == (4, 7) or pos == (4, 0):
        y = pos[1]

        # Roque pequeno (lado do rei)
        if game.board[y][5] == 0 and game.board[y][6] == 0:
          if (game.castling[0] == 1 and player == 1) or (game.castling[2] == 1 and player == -1):
            result.append((6, y))

        # Roque grande (lado da dama)
        if game.board[y][3] == 0 and game.board[y][2] == 0:
          if (game.castling[1] == 1 and player == 1) or (game.castling[3] == 1 and player == -1):
            result.append((2, y))

      return result # Retorna a lista com as jogadas possíveis