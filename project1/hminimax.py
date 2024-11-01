from pacman_module.game import Agent, Directions
from pacman_module.util import manhattanDistance


class PacmanAgent(Agent):
    """Pacman agent using H-Minimax."""

    def __init__(self):
        super().__init__()
        self.depth = 3
        self.visit_count = {}

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move."""
        _, action = self.hMinimax(state, self.depth, is_pacman_turn=True)

        return action if action else Directions.STOP

    def hMinimax(self, state, depth, is_pacman_turn):
        """Performs H-Minimax without alpha-beta pruning."""

        # If cutoff, return the evaluation value
        if self.isCutOff(state, depth):
            eval_value = self.evaluate_state(state)
            return eval_value, None

        if is_pacman_turn:
            return self.max_value(state, depth)
        else:
            return self.min_value(state, depth)

    def max_value(self, state, depth):
        """Fonction max pour Pacman (survivre et ramasser la nourriture)."""
        v = float('-inf')
        best_action = None

        for successor_state, action in state.generatePacmanSuccessors():
            min_val, _ = self.hMinimax(
                successor_state, depth - 1, is_pacman_turn=False
            )
            if min_val > v:
                v = min_val
                best_action = action

        return v, best_action

    def min_value(self, state, depth):
        """Fonction min pour les fantômes (réduire le score de Pacman)."""
        v = float('inf')
        best_action = None

        for successor_state, action in state.generateGhostSuccessors(1):
            max_val, _ = self.hMinimax(
                successor_state, depth - 1, is_pacman_turn=True
            )
            if max_val < v:
                v = max_val
                best_action = action

        return v, best_action

    def isTerminal(self, state):
        """Checks if the state is terminal (win or lose)."""
        return state.isWin() or state.isLose()

    def isCutOff(self, state, depth):
        """Checks if the search should be cut off."""
        return depth == 0 or self.isTerminal(state)

    def evaluate_state(self, state):
        """Evaluate the state by considering both
        food and ghost."""
        pacman_pos = state.getPacmanPosition()
        ghost_positions = state.getGhostPositions()
        food_positions = state.getFood().asList()

        # Calculate minimum distance to ghosts
        min_ghost_distance = min(
            manhattanDistance(pacman_pos, ghost_pos)
            for ghost_pos in ghost_positions
        ) if ghost_positions else float('inf')

        # Calculate minimum distance to food
        min_food_distance = min(
            manhattanDistance(pacman_pos, food_pos)
            for food_pos in food_positions
        ) if food_positions else 1

        # Higher penalty for being close to ghosts
        ghost_penalty = -25 / (
            min_ghost_distance + 1
            ) if min_ghost_distance < 3 else -5 / (min_ghost_distance + 1)

        # Higher reward for getting closer to food
        if min_food_distance < 3:
            food_reward = 35 / (min_food_distance + 1)
        else:
            food_reward = 30 / (min_food_distance + 1)

        # Incremental revisit penalty based on visit count
        self.visit_count[pacman_pos] = self.visit_count.get(pacman_pos, 0) + 1
        visit_penalty = -self.visit_count[pacman_pos]

        # If Pacman is close to both food and ghosts, prioritize food
        # I think that that is a good idea to prioritize food
        if min_food_distance < 3 and min_ghost_distance < 3:
            ghost_penalty = -5

        dynamic_penalty = ghost_penalty + visit_penalty

        return 10 * state.getScore() + dynamic_penalty + food_reward
