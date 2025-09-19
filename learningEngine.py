import json
import os
from chessTable import ChessTable

class LearningEngine(ChessTable):
    def __init__(self, pst_file="pst.json", state='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'):
        super().__init__(state=state)
        self.pst_file = pst_file
        self.load_pst()

    def load_pst(self):
        if os.path.exists(self.pst_file):
            with open(self.pst_file, "r") as f:
                self.pst = json.load(f)
        else:
            self.pst = {str(i): [[0 for _ in range(8)] for _ in range(8)] for i in range(1, 7)}

    def save_weights(self):
        with open(self.pst_file, 'w') as f:
            json.dump(self.pst, f, indent=4)

    def piece_score(self, piece_id, y, x):
        # Retorna o peso de uma peça junto com o valor de sua posição
        return self.weights[piece_id] * self.pst[str(piece_id)][y][x]

    def adjust_weights(self, move_history, learning_rate=0.01):
        # Ajusta os pesos com base no número de jogadas a partir da posição de destino de cada movimento
        for move in move_history:
            id = move[0]
            x, y = move[1]
            num_moves = move[2]
            self.pst[str(id)][y][x] += (num_moves + self.weights[id]) * learning_rate
        self.save_weights()