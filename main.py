# @title Main

import copy
import math
import random
import time
import pandas as pd
import matplotlib.pyplot as plt
from chessTable import ChessTable
from learningEngine import LearningEngine
from minimax import choose_best_move, get_search_stats
from pieces import *

# Configuration Functions
def get_ai_settings():
    """Get AI depth and time limit settings from user input."""
    ai_depth = int(input("Digite a profundidade da IA (padrão 3): ") or "3")
    time_limit_input = input("Digite o limite de tempo da IA em segundos (Enter para sem limite): ")
    ai_time_limit = float(time_limit_input) if time_limit_input else None
    return ai_depth, ai_time_limit

def get_ai_vs_ai_settings():
    """Get settings for both AIs in AI vs AI mode."""
    depth_white = int(input("Digite a profundidade da IA das Brancas (0 para aleatório): "))
    depth_black = int(input("Digite a profundidade da IA das Pretas (0 para aleatório): "))
    
    time_limit_white_input = input("Digite o limite de tempo para IA Brancas em segundos (Enter para sem limite): ")
    time_limit_white = float(time_limit_white_input) if time_limit_white_input else None
    
    time_limit_black_input = input("Digite o limite de tempo para IA Pretas em segundos (Enter para sem limite): ")
    time_limit_black = float(time_limit_black_input) if time_limit_black_input else None
    
    return depth_white, depth_black, time_limit_white, time_limit_black

# Game State Functions
def check_game_end(game):
    """Check if the game has ended and return the result."""
    # Check 50-move rule
    if game.halfmove_clock >= 100:
        return "50_move_draw"
    
    legal_moves = game.generate_legal_moves(game.p_move)
    if not legal_moves:
        if game.is_in_check(game.p_move):
            return "checkmate"
        else:
            return "stalemate"
    
    return None

def print_game_end_message(result, current_player):
    """Print the appropriate message for game end."""
    if result == "50_move_draw":
        print("Empate! (Regra das 50 jogadas)")
    elif result == "checkmate":
        print("Cheque-mate!")
        winner = "Pretas" if current_player == 1 else "Brancas"
        print("Vitória de:", winner)
    elif result == "stalemate":
        print("Empate (afogamento)!")

def get_state(game):
    """Generate a string representation of the current game state."""
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

# Move Formatting Functions
def format_time_info(thinking_time, time_limit):
    """Format the time information for move display."""
    time_info = f"tempo: {thinking_time:.3f}s"
    if time_limit:
        time_info += f"/{time_limit}s"
    return time_info

def format_depth_info(actual_depth, target_depth, time_limited=False):
    """Format the depth information for move display."""
    depth_info = f"profundidade: {actual_depth}"
    if actual_depth < target_depth and time_limited:
        depth_info += f"/{target_depth} (limitado por tempo)"
    elif target_depth > 0:
        depth_info += f"/{target_depth}"
    return depth_info

def format_move_info(player_name, move_uci, thinking_time, time_limit, stats, target_depth):
    """Format complete move information for display."""
    time_info = format_time_info(thinking_time, time_limit)
    depth_info = format_depth_info(stats['actual_depth'], target_depth, time_limit is not None)
    
    return f"Jogador {player_name} moveu: {move_uci} ({time_info}, {depth_info}, {stats['nodes_searched']} jogadas analisadas)"

# Move Execution Functions
def execute_ai_move(game, depth, time_limit):
    """Execute an AI move and return move info."""
    start_time = time.time()
    
    if depth == 0:
        move = game.choose_random_move()
        thinking_time = 0.0
        return move, thinking_time, None
    else:
        move = choose_best_move(game, depth=depth, max_time=time_limit)
        end_time = time.time()
        thinking_time = end_time - start_time
        stats = get_search_stats()
        return move, thinking_time, stats

def try_make_move(game, move, player_name):
    """Try to make a move with error handling and fallback."""
    try:
        return game.make_move(move)
    except ValueError as e:
        print(f"ERRO: {e}")
        print(f"Tentando movimento de fallback para {player_name}...")
        
        # Fallback to a random legal move
        legal_moves = game.generate_legal_moves(game.p_move)
        if legal_moves:
            fallback_move = legal_moves[0]
            print(f"Usando movimento de fallback: {game.move_to_uci(fallback_move)}")
            return game.make_move(fallback_move)
        else:
            print("Nenhum movimento legal disponível. Terminando jogo.")
            return False

def handle_player_move(game, legal_moves):
    """Handle player input and move validation."""
    legal_uci = [game.move_to_uci(m) for m in legal_moves]
    print("Movimentos legais:", legal_uci)
    
    user_input = input("Digite seu movimento (UCI, ex: e7e5): ")
    uci_move = game.uci_to_move(user_input)
    
    try:
        if uci_move in legal_moves:
            game.make_move(uci_move)
            return True
        else:
            print("Movimento inválido, tente novamente!")
            return False
    except:
        print("Entrada inválida, tente novamente!")
        return False

def play_ai_turn(game, ai_depth, ai_time_limit):
    """Handle AI turn in player vs AI mode."""
    print("\nIA pensando...")
    move, thinking_time, stats = execute_ai_move(game, ai_depth, ai_time_limit)
    
    if move:
        game.make_move(move)
        
        # Format and display move info
        time_info = format_time_info(thinking_time, ai_time_limit)
        
        depth_info = ""
        if ai_time_limit and stats and stats['actual_depth'] < ai_depth:
            depth_info = f", profundidade: {stats['actual_depth']}/{ai_depth} (limitado por tempo)"
        elif ai_time_limit and stats:
            depth_info = f", profundidade: {stats['actual_depth']}/{ai_depth}"
        
        nodes_info = f", {stats['nodes_searched']} jogadas analisadas" if stats else ""
        print(f"IA jogou: {game.move_to_uci(move)} ({time_info}{depth_info}{nodes_info})")
        return True
    else:
        print("Nenhuma jogada possível!")
        return False

def play_human_turn(game):
    """Handle human player turn."""
    print("\nSeu turno (Pretas)!")
    legal_moves = game.generate_legal_moves(game.p_move)
    return handle_player_move(game, legal_moves)

def main_player_vs_ai():
    """Main function for Player vs AI game mode."""
    game = ChessTable()
    
    print("=== Xadrez: Player vs IA ===")
    print("Você joga de Pretas! (digite os lances no formato UCI, ex: e7e5)")
    
    ai_depth, ai_time_limit = get_ai_settings()
    print()
    
    while True:
        game.display()
        
        # Check for game end conditions
        game_result = check_game_end(game)
        if game_result:
            print_game_end_message(game_result, game.p_move)
            break
        
        # Handle turns based on current player
        if game.p_move == 1:  # AI turn (White)
            if not play_ai_turn(game, ai_depth, ai_time_limit):
                break
        else:  # Human turn (Black)
            if not play_human_turn(game):
                continue  # Invalid move, try again

def play_ai_vs_ai_turn(game, depth, time_limit, turn_number):
    """Handle a single turn in AI vs AI mode."""
    player_name = "Brancas" if game.p_move == 1 else "Pretas"
    print(f"\nTurno {turn_number}: Jogador {player_name} pensando...")
    
    # Execute the move
    move, thinking_time, stats = execute_ai_move(game, depth, time_limit)
    
    if move is None:
        # Handle no moves available
        if game.is_in_check(game.p_move):
            print(f"Cheque-mate! Jogador {player_name} perdeu.")
        else:
            print("Empate! Afogamento.")
        return False
    
    # Display move information
    if depth == 0:
        print(f"Jogador {player_name} moveu: {game.move_to_uci(move)} (aleatório)")
    else:
        move_info = format_move_info(player_name, game.move_to_uci(move), thinking_time, time_limit, stats, depth)
        print(move_info)
    
    # Try to make the move
    info = try_make_move(game, move, player_name)
    if info:
        return info,thinking_time, stats['nodes_searched']
    else:
        return False,thinking_time, stats['nodes_searched']

def main_ai_vs_ai():
    """Main function for AI vs AI game mode."""
    game = ChessTable()
    game.display()
    
    depth_white, depth_black, time_limit_white, time_limit_black = get_ai_vs_ai_settings()
    
    turn = 0
    while True:
        # Check for game end conditions
        game_result = check_game_end(game)
        if game_result:
            print_game_end_message(game_result, game.p_move)
            break
        
        # Get current player's settings
        current_depth = depth_white if game.p_move == 1 else depth_black
        current_time_limit = time_limit_white if game.p_move == 1 else time_limit_black
        
        # Play the turn
        success, thinking_time, nodes_searched =  play_ai_vs_ai_turn(game, current_depth, current_time_limit, turn)
        if not success:
            break
        
        game.display()
        turn += 1

def get_game_mode():
    """Get the game mode from user input."""
    while True:
        try:
            mode = input("Digite 1 para Player vs I, 2 para IA vs IA ou 3 para realizar um experimento: ")
            if mode in ["1", "2", "3"]:
                return mode
            else:
                print("Por favor, digite 1,2 ou 3.")
        except (EOFError, KeyboardInterrupt):
            print("\nSaindo do jogo.")
            return None

def main_experimentos():
    """Executa N jogos entre IA vs IA, coleta estatísticas e gera gráficos."""
    try:
        N = int(input("Digite a quantidade de jogos a serem simulados: "))
    except ValueError:
        print("Entrada inválida. Usando N=10 por padrão.")
        N = 10

    depth_white, depth_black, time_limit_white, time_limit_black = get_ai_vs_ai_settings()

    resultados = []
    metricas = []
    for i in range(N):
        print(f"\n=== Jogo {i+1}/{N} ===")
        game = LearningEngine()
        turn = 0
        move_history = []

        while True:
            game_result = check_game_end(game)
            if game_result:
                if game_result == "checkmate":
                    winner = "Pretas" if game.p_move == 1 else "Brancas"
                elif game_result == "stalemate":
                    winner = "Empate"
                elif game_result == "50_move_draw":
                    winner = "Empate"
                else:
                    winner = "Desconhecido"

                resultados.append({
                    "jogo": i+1,
                    "prof_brancas": depth_white,
                    "prof_pretas": depth_black,
                    "vencedor": winner
                })
                metricas.append({
                    "jogo": i+1,
                    "turno": turn,
                    "jogador": player_name,
                    "tempo_pensando": thinking_time,
                    "jogadas_analisadas": nodes_searched,
                })
                break

            # Escolhe profundidade e tempo do jogador atual
            current_depth = depth_white if game.p_move == 1 else depth_black
            current_time_limit = time_limit_white if game.p_move == 1 else time_limit_black
            player_name = "Brancas" if game.p_move == 1 else "Pretas"

            # Jogada da IA
            info, thinking_time, nodes_searched =  play_ai_vs_ai_turn(game, current_depth, current_time_limit, turn)
            if not info:
                resultados.append({
                    "jogo": i+1,
                    "prof_brancas": depth_white,
                    "prof_pretas": depth_black,
                    "vencedor": "Erro/Interrompido"
                })
                break
            
            metricas.append({
                "jogo": i+1,
                "turno": turn,
                "jogador": player_name,
                "tempo_pensando": thinking_time,
                "jogadas_analisadas": nodes_searched,
            })
            piece_id = abs(int(info['moved']))
            cls_name = game.parts[piece_id]
            piece_cls = globals()[cls_name]
            target = info['move'][1]
            poss = piece_cls.movement(game, game.p_move, target, capture=True)
            move_history.append((piece_id, target, len(poss)))
            turn += 1
        game.adjust_weights(move_history)

    # Converte para DataFrame para análise
    df_result = pd.DataFrame(resultados)
    df_metricas = pd.DataFrame(metricas)
    df_media = df_metricas.groupby(["jogo", "jogador"]).agg({
        "tempo_pensando": "mean",
        "jogadas_analisadas": "mean"
        }).reset_index()

    print("\n=== Resultados ===")
    print(df_result)

    # Estatísticas gerais
    vitorias_brancas = (df_result["vencedor"] == "Brancas").sum()
    vitorias_pretas = (df_result["vencedor"] == "Pretas").sum()
    empates = (df_result["vencedor"] == "Empate").sum()

    print(f"\nVitórias Brancas: {vitorias_brancas}")
    print(f"Vitórias Pretas: {vitorias_pretas}")
    print(f"Empates: {empates}")

    # Exibir gráficos
    
    while True:
        N = int(input("Digite 1 para visualizar o grásfico de análise de vitórias ou \n digite 2 para visualizar o gráfico de análise de tempo para escolher uma jogada ou \n digite 3 para vizualisar o gráfico de análise da quantidade de jogadas analisadas ou \n digite 4 para encerrar a análise: "))
        if (N == 1):
            df_result["vencedor"].value_counts().plot(kind="bar", color=["blue", "black", "gray"])
            plt.title("Distribuição de Resultados")
            plt.xlabel("Resultado")
            plt.ylabel("Quantidade de Jogos")
            plt.show()
        elif (N == 2):
            plt.figure(figsize=(10,6))
            for jogador, dados in df_media.groupby("jogador"):
                plt.plot(dados["jogo"], dados["tempo_pensando"], marker="o", label=jogador)
            plt.title("Tempo médio de cálculo por partida")
            plt.xlabel("Partida")
            plt.ylabel("Tempo médio (s)")
            plt.legend()
            plt.grid(True)
            plt.show()

        elif (N == 3):
            plt.figure(figsize=(10,6))
            for jogador, dados in df_media.groupby("jogador"):
                plt.plot(dados["jogo"], dados["jogadas_analisadas"], marker="o", label=jogador)
            plt.title("Média de jogadas analisadas por partida")
            plt.xlabel("Partida")
            plt.ylabel("Jogadas analisadas (média)")
            plt.legend()
            plt.grid(True)
            plt.show()
        elif (N == 4): break
        
        else: print("Entrada inválida")

if __name__ == "__main__":
    mode = get_game_mode()
    if mode == "1":
        main_player_vs_ai()
    elif mode == "2":
        main_ai_vs_ai()
    elif mode == "3":
        main_experimentos()
