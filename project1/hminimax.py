from pacman_module.game import Agent, Directions
from pacman_module.util import manhattanDistance


def key(state, layer=None):
    """Returns a key that uniquely identifies a Pacman game state."""
    return (
        state.getPacmanPosition(),
        state.getFood(),
        state.getGhostPosition(1),
        state.getScore(),
        layer
    )


class PacmanAgent(Agent):
    """Pacman agent using H-Minimax with alpha-beta pruning."""

    def __init__(self):
        super().__init__()
        self.depth = 15
        self.transposition_table = {}

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move."""
        _, action = self.h_minimax(state, self.depth, "survival")
        return action if action else Directions.STOP

    def h_minimax(self, state, depth, layer):
        """Performs H-Minimax with alpha-beta pruning."""
        if layer == "survival":
            return self.survival_max_value(
                state, float('-inf'), float('inf'), depth, next_layer="food"
                )
        else:
            return self.food_min_value(
                state, float(
                    '-inf'), float('inf'), depth, next_layer="survival"
                )

    def survival_max_value(self, state, alpha, beta, depth, next_layer):
        """Max value function focused on survival."""
        state_key = key(state, "survival")
        if state_key in self.transposition_table:
            return self.transposition_table[state_key]

        if self.is_terminal_state(state) or self.cutoff_test(state, depth):
            eval_value = self.survival_eval_function(state)
            self.transposition_table[state_key] = (eval_value, None)
            return eval_value, None

        v = float('-inf')
        best_action = None
        for action in state.getLegalActions():
            successor = state.generateSuccessor(0, action)
            min_val, _ = self.food_min_value(
                successor, alpha, beta, depth - 1, next_layer="survival"
                )
            if min_val > v:
                v = min_val
                best_action = action
            if v >= beta:
                self.transposition_table[state_key] = (v, action)
                return v, action
            alpha = max(alpha, v)

        self.transposition_table[state_key] = (v, best_action)
        return v, best_action

    def food_min_value(self, state, alpha, beta, depth, next_layer):
        """Min value function focused on food collection."""
        state_key = key(state, "food")
        if state_key in self.transposition_table:
            return self.transposition_table[state_key]

        if self.is_terminal_state(state) or self.cutoff_test(state, depth):
            eval_value = self.food_eval_function(state)
            self.transposition_table[state_key] = (eval_value, None)
            return eval_value, None

        v = float('inf')
        best_action = None
        for action in state.getLegalActions(1):
            successor = state.generateSuccessor(1, action)
            max_val, _ = self.survival_max_value(
                successor, alpha, beta, depth - 1, next_layer="food"
                )
            if max_val < v:
                v = max_val
                best_action = action
            if v <= alpha:
                self.transposition_table[state_key] = (v, action)
                return v, action
            beta = min(beta, v)

        self.transposition_table[state_key] = (v, best_action)
        return v, best_action

    def is_terminal_state(self, state):
        """Checks if the state is terminal (win or lose)."""
        return state.isWin() or state.isLose()

    def cutoff_test(self, state, depth):
        """cutoff for depth."""
        return depth == 0

    def survival_eval_function(self, state):
        """Evaluate survival by penalizing proximity to ghosts."""
        pacman_pos = state.getPacmanPosition()
        ghost_positions = state.getGhostPositions()
        min_ghost_distance = min(
            manhattanDistance(
                pacman_pos, ghost_pos
                ) for ghost_pos in ghost_positions
        ) if ghost_positions else float('inf')

        # Ghost penalty calculation
        ghost_penalty = 20
        if min_ghost_distance < 3:
            ghost_penalty = -10 * (3 - min_ghost_distance)

        return ghost_penalty + state.getScore()

    def food_eval_function(self, state):
        """Evaluate food by encouraging proximity to food."""
        pacman_pos = state.getPacmanPosition()
        food_positions = state.getFood().asList()
        min_food_distance = min(
            manhattanDistance(
                pacman_pos, food_pos
                ) for food_pos in food_positions
        ) if food_positions else 0

        return state.getScore() - min_food_distance
