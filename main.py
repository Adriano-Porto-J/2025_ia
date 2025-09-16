# @title Main

import copy
import math
import random
import time
from chessTable import ChessTable
from minimax import choose_best_move, get_search_stats

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
    print("Você joga de Pretas! (digite os lances no formato UCI, ex: e7e5)")
    
    # Configurar ajustes da IA
    ai_depth = int(input("Digite a profundidade da IA (padrão 3): ") or "3")
    time_limit_input = input("Digite o limite de tempo da IA em segundos (Enter para sem limite): ")
    ai_time_limit = float(time_limit_input) if time_limit_input else None
    print()

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
            start_time = time.time()
            move = choose_best_move(game, depth=ai_depth, max_time=ai_time_limit)
            end_time = time.time()
            thinking_time = end_time - start_time
            
            if move:
                game.make_move(move)
                stats = get_search_stats()
                time_info = f"tempo: {thinking_time:.3f}s"
                if ai_time_limit:
                    time_info += f"/{ai_time_limit}s"
                
                depth_info = ""
                if ai_time_limit and stats['actual_depth'] < ai_depth:
                    depth_info = f", profundidade: {stats['actual_depth']}/{ai_depth} (limitado por tempo)"
                elif ai_time_limit:
                    depth_info = f", profundidade: {stats['actual_depth']}/{ai_depth}"
                
                print(f"IA jogou: {game.move_to_uci(move)} ({time_info}{depth_info}, {stats['nodes_searched']} jogadas analisadas)")
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
    
    # Configurar limites de tempo
    time_limit_white_input = input("Digite o limite de tempo para IA Brancas em segundos (Enter para sem limite): ")
    time_limit_white = float(time_limit_white_input) if time_limit_white_input else None
    
    time_limit_black_input = input("Digite o limite de tempo para IA Pretas em segundos (Enter para sem limite): ")
    time_limit_black = float(time_limit_black_input) if time_limit_black_input else None

    turn = 0
    while True:
        if game.halfmove_clock >= 100:
            print("Empate! (Regra das 50 jogadas)")
            break

        player_name = "Brancas" if game.p_move == 1 else "Pretas"
        print(f"\nTurno {turn}: Jogador {player_name} pensando...")

        current_depth = depth_white if game.p_move == 1 else depth_black
        current_time_limit = time_limit_white if game.p_move == 1 else time_limit_black

        start_time = time.time()
        if current_depth == 0:
            move = game.choose_random_move()
            thinking_time = 0.0  # Movimentos aleatórios são instantâneos
        else:
            move = choose_best_move(game, depth=current_depth, max_time=current_time_limit)
            end_time = time.time()
            thinking_time = end_time - start_time

        if move is None:
            if game.is_in_check(game.p_move):
                print("Cheque-mate! Jogador", player_name, "perdeu.")
            else:
                print("Empate! Afogamento.")
            break

        if current_depth == 0:
            print(f"Jogador {player_name} moveu: {game.move_to_uci(move)} (aleatório)")
        else:
            stats = get_search_stats()
            time_info = f"tempo: {thinking_time:.3f}s"
            if current_time_limit:
                time_info += f"/{current_time_limit}s"
            
            depth_info = f"profundidade: {stats['actual_depth']}"
            if stats['actual_depth'] < current_depth:
                depth_info += f"/{current_depth} (limitado por tempo)"
            else:
                depth_info += f"/{current_depth}"
            
            print(f"Jogador {player_name} moveu: {game.move_to_uci(move)} ({time_info}, {depth_info}, {stats['nodes_searched']} jogadas analisadas)")
        
        # Attempt to make the move with error handling
        try:
            game.make_move(move)
        except ValueError as e:
            print(f"ERRO: {e}")
            print(f"Tentando movimento de fallback para {player_name}...")
            # Fallback to a random legal move
            legal_moves = game.generate_legal_moves(game.p_move)
            if legal_moves:
                fallback_move = legal_moves[0]
                print(f"Usando movimento de fallback: {game.move_to_uci(fallback_move)}")
                game.make_move(fallback_move)
            else:
                print("Nenhum movimento legal disponível. Terminando jogo.")
                break
        
        game.display()
        turn += 1

if __name__ == "__main__":
    modo = input("Digite 1 para Player vs IA ou 2 para IA vs IA: ")
    if modo == "1":
        main_player_vs_ai()
    else:
        main_ai_vs_ai()