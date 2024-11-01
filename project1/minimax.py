from pacman_module.game import Agent, Directions
from pacman_module.util import manhattanDistance


class PacmanAgent(Agent):
    """Pacman agent using Minimax with a transposition table."""

    def __init__(self):
        super().__init__()
        self.visit_count = {}

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move."""
        _, action = self.minimax(state, is_pacman_turn=True)

        # Update the visit count for Pacman's current position
        pacman_pos = state.getPacmanPosition()
        if pacman_pos in self.visit_count:
            # Increment the visit count (higher penalty for revisits)
            self.visit_count[pacman_pos] += 10
        else:
            self.visit_count[pacman_pos] = 1

        return action if action else Directions.STOP

    def minimax(self, state, is_pacman_turn):
        """Performs Minimax."""

        # If the state is terminal, return the utility value
        if self.isTerminal(state):
            utility_value = self.utility(state)
            return utility_value, None

        if is_pacman_turn:
            return self.max_value(state)
        else:
            return self.min_value(state)

    def max_value(self, state):
        """Max value function for Pacman
        (trying to survive and collect food)."""
        v = float('-inf')
        best_action = None

        for successor_state, action in state.generatePacmanSuccessors():
            min_val, _ = self.minimax(
                successor_state, is_pacman_turn=False
            )
            if min_val > v:
                v = min_val
                best_action = action

        return v, best_action

    def min_value(self, state):
        """Min value function for ghosts
        (trying to minimize Pacman's score)."""
        v = float('inf')
        best_action = None

        for successor_state, action in state.generateGhostSuccessors(1):
            max_val, _ = self.minimax(
                successor_state, is_pacman_turn=True
            )
            if max_val < v:
                v = max_val
                best_action = action

        return v, best_action

    def isTerminal(self, state):
        """Checks if the state is terminal (win or lose)."""
        return state.isWin() or state.isLose()

    def utility(self, state):
        """Returns the utility value of a Pacman game state."""
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
            food_reward = 30 / (min_food_distance + 1)
        else:
            food_reward = 35 / (min_food_distance + 1)

        # Incremental revisit penalty based on visit count
        visit_penalty = -5 * self.visit_count.get(pacman_pos, 0)

        # If Pacman is close to both food and ghosts, prioritize food
        # I think that that is a good idea to prioritize food
        if min_food_distance < 3 and min_ghost_distance < 3:
            ghost_penalty = - 5

        return state.getScore() + ghost_penalty + food_reward + visit_penalty
