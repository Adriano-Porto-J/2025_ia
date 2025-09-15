# @title Main

import copy
import math
import random
from chessTable import ChessTable
from minimax import choose_best_move

def get_state(game):
    piece_map = {0: '.', 1: 'P', 2: 'N', 3: 'B', 4: 'R', 5: 'Q', 6: 'K'}
    state = ""
    for row in game.board:
        for piece in row:
            if piece == 0:
                state += '.'
            else:
                ch = piece_map[abs(piece)]
                if piece < 0:
                    ch = ch.lower()
                state += ch
    state += str(game.p_move)
    return state

def main_player_vs_ai():
    game = ChessTable()

    print("=== Xadrez: Player vs IA ===")
    print("Você joga de Pretas! (digite os lances no formato UCI, ex: e7e5)\n")

    while True:
        game.display()

        # Verificação da regra de empate de 50 jogadas
        if game.halfmove_clock >= 100:
            print("Empate! (Regra das 50 jogadas)")
            break

        legal = game.generate_legal_moves(game.p_move)

        if not legal:
            if game.is_in_check(game.p_move):
                print("Cheque-mate!")
                vencedor = "Pretas" if game.p_move == 1 else "Brancas"
                print("Vitória de:", vencedor)
            else:
                print("Empate (afogamento)!")
            break

        if game.p_move == 1:
            print("\nIA pensando...")
            move = choose_best_move(game, depth=3)
            if move:
                game.make_move(move)
                print("IA jogou:", game.move_to_uci(move))
            else:
                print("Nenhuma jogada possível!")
                break
        else:  # vez do jogador (pretas)
            print("\nSeu turno (Pretas)!")
            legal_uci = [game.move_to_uci(m) for m in legal]
            print("Movimentos legais:", legal_uci)
            uci_move = game.uci_to_move(input("Digite seu movimento (UCI, ex: e7e5): "))
            try:
                if uci_move in legal:
                    game.make_move(uci_move)
                else:
                    print("Movimento inválido, tente novamente!")
            except:
                print("Entrada inválida, tente novamente!")

def main_ai_vs_ai():
    game = ChessTable()
    game.display()

    depth_white = int(input("Digite a profundidade da IA das Brancas (0 para aleatório): "))
    depth_black = int(input("Digite a profundidade da IA das Pretas (0 para aleatório): "))

    turn = 0
    while True:
        if game.halfmove_clock >= 100:
            print("Empate! (Regra das 50 jogadas)")
            break

        player_name = "Brancas" if game.p_move == 1 else "Pretas"
        print(f"\nTurno {turn}: Jogador {player_name} pensando...")

        current_depth = depth_white if game.p_move == 1 else depth_black

        if current_depth == 0:
            move = game.choose_random_move()
        else:
            move = choose_best_move(game, depth=current_depth)  # <- chama Minimax separado

        if move is None:
            if game.is_in_check(game.p_move):
                print("Cheque-mate! Jogador", player_name, "perdeu.")
            else:
                print("Empate! Afogamento.")
            break

        print(f"Jogador {player_name} moveu: {game.move_to_uci(move)}")
        game.make_move(move)
        game.display()
        turn += 1

if __name__ == "__main__":
    modo = input("Digite 1 para Player vs IA ou 2 para IA vs IA: ")
    if modo == "1":
        main_player_vs_ai()
    else:
        main_ai_vs_ai()