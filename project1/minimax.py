from pacman_module.game import Agent, Directions
from pacman_module.util import manhattanDistance


def key(state):
    """Returns a key that uniquely identifies a Pacman game state.

    Arguments:
        state: a game state. See API or class `pacman.GameState`.

    Returns:
        A hashable key tuple.
    """

    return (
        state.getPacmanPosition(),
        state.getFood(),
        state.getGhostPosition(1),
        state.getScore(),
        # ...
    )


class PacmanAgent(Agent):
    """Pacman agent using Minimax with alpha-beta pruning."""

    def __init__(self):
        super().__init__()
        self.moves = None
        self.depth = 7
        self.transposition_table = {}

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move.

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A legal move as defined in `game.Directions`.
        """
        self.moves = self.minimax(state)

        if self.moves:
            move = self.moves.pop(0)
            return move
        else:
            return Directions.STOP

    def minimax(self, state):
        """Perform Minimax search with alpha-beta pruning.

        Args:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A list of legal moves.
        """
        _, action = self.alpha_beta_search(state, self.depth)
        return [action] if action else []

    def alpha_beta_search(self, state, depth):
        """Alpha-beta pruning search.

        Args:
            state: a game state. See API or class `pacman.GameState`.
            depth: current depth of the search.

        Returns:
            The best action determined by the Minimax algorithm.
        """
        v, action = self.max_value(state, float('-inf'), float('inf'), depth)
        return v, action

    def max_value(self, state, alpha, beta, depth):
        """Max value function for Minimax with alpha-beta pruning.
        Code inspired from the pseudo code in the course.

        Args:
            state: a game state. See API or class `pacman.GameState`.
            alpha: alpha value for pruning.
            beta: beta value for pruning.
            depth: current depth of the search.

        Returns:
            The utility value and the corresponding action.
        """
        # Check if the state is already in the transposition table
        state_key = key(state)
        if state_key in self.transposition_table:
            return self.transposition_table[state_key]

        # Check if the state is a terminal state
        if state.isWin() or state.isLose() or depth == 0:
            utility_value = self.utility(state)
            self.transposition_table[state_key] = utility_value, None
            return utility_value, None

        v = float('-inf')
        best_action = None
        for action in state.getLegalActions():
            successor = state.generateSuccessor(0, action)
            min_val, _ = self.min_value(successor, alpha, beta, depth - 1)
            if min_val > v:
                v = min_val
                best_action = action
            if v >= beta:
                self.transposition_table[state_key] = v, action
                return v, action
            alpha = max(alpha, v)

        # Store the best action in the transposition table
        self.transposition_table[state_key] = v, best_action
        return v, best_action

    def min_value(self, state, alpha, beta, depth):
        """Min value function for Minimax with alpha-beta pruning.

        Args:
            state: a game state. See API or class `pacman.GameState`.
            alpha: alpha value for pruning.
            beta: beta value for pruning.
            depth: current depth of the search.

        Returns:
            The utility value and the corresponding action.
            Code inspired from the pseudo code in the course.
        """
        # Check if the state is already in the transposition table
        state_key = key(state)
        if state_key in self.transposition_table:
            return self.transposition_table[state_key]

        # Check if the state is a terminal state
        if state.isWin() or state.isLose() or depth == 0:
            utility_value = self.utility(state)
            self.transposition_table[state_key] = utility_value, None
            return utility_value, None

        v = float('inf')
        best_action = None
        for action in state.getLegalActions(1):
            successor = state.generateSuccessor(1, action)
            max_val, _ = self.max_value(successor, alpha, beta, depth - 1)
            if max_val < v:
                v = max_val
                best_action = action
            if v <= alpha:
                self.transposition_table[state_key] = v, action
                return v, action
            beta = min(beta, v)

        self.transposition_table[state_key] = v, best_action
        return v, best_action

    def utility(self, state):
        """Utility function to evaluate game states."""
        pacman_pos = state.getPacmanPosition()
        food = state.getFood()
        food_positions = food.asList()
        ghost_positions = state.getGhostPositions()

        # Calculate the Manhattan distance to the nearest food pellet
        min_food_distance = min(
            manhattanDistance(
                pacman_pos, food_pos
                ) for food_pos in food_positions
            ) if food_positions else 0

        # Calculate the Manhattan distance to the nearest ghost
        min_ghost_distance = min(
            manhattanDistance(
                pacman_pos, ghost_pos
                ) for ghost_pos in ghost_positions
            ) if ghost_positions else float('inf')

        # Penalty for being close to a ghost
        if min_ghost_distance < 3:
            ghost_penalty = -10 * (3 - min_ghost_distance)
        else:
            ghost_penalty = 0

        utility_value = state.getScore() - min_food_distance + ghost_penalty
        return utility_value
