# @title LearningEngine

import json
import os
from chessTable import ChessTable

class LearningEngine(ChessTable):
    def __init__(self, pst_file="weights.json", state='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'):
        super().__init__(state=state)
        self.pst_file = pst_file
        self.load_pst()

    def load_pst(self, path= "values.json"):
        if os.path.exists(path):
            with open(path, "r") as f:
                self.pst = json.load(f)
        else:
            table = [[0] * 8] * 8
            self.pst = {i: table for i in range(1, 7)}

    def save_weights(self):
        with open(self.pst_file, 'w') as f:
            json.dump(self.pst, f, indent=4)

    def piece_score(self, piece_id, y, x):
        return self.weights[piece_id] + self.pst[piece_id][y][x]

    def adjust_weights(self, result, learning_rate=0.01):
        """
        Ajusta os pesos com base no histórico de posições da partida.
        """
        for state in self.history:

            # Avalie a posição do histórico
            score_at_state = self.evaluate(state)

            # Use o erro para ajustar os pesos
            error = result - score_at_state

            # Ajuste os pesos com base nas peças presentes nesta posição específica
            for y in range(8):
                for x in range(8):
                    piece = state.board[y][x]
                    if piece == 0:
                        continue
                    piece_type = abs(piece)
                    sign = 1 if piece > 0 else -1

                    self.pst[piece_type][y][x] += learning_rate * error * sign

        self.save_weights()