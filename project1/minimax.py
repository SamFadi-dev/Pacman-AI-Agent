from pacman_module.game import Agent, Directions
from pacman_module.util import manhattanDistance
import sys
sys.setrecursionlimit(10**6)


class PacmanAgent(Agent):
    """Pacman agent using Minimax with a transposition table."""

    def __init__(self):
        super().__init__()

    def get_action(self, state):
        """Get the best action for Pacman using Minimax."""
        closed_states = set()

        successors = list(state.generatePacmanSuccessors())

        if not successors:
            return Directions.STOP

        best_action = max(
            successors,
            key=lambda sa: self.evaluate_successor(sa, closed_states)
        )[1]

        return best_action

    def evaluate_successor(self, state_action, closed_states):
        """Evaluate the successor state using Minimax."""
        state, _ = state_action
        key = self.key(state)
        closed_states.add(key)
        score = self.minimax(state, False, closed_states)
        closed_states.remove(key)
        return score

    def minimax(self, state, is_pacman_turn, closed_states):
        """Minimax algorithm implementation."""
        # Check if the state is terminal
        if self.isTerminal(state):
            return state.getScore()
        return (
            self.max_value(state, closed_states)
            if is_pacman_turn else
            self.min_value(state, closed_states)
        )

    def max_value(self, state, closed_states):
        """Maximizing function for Pacman's turn."""
        v = float('-inf')
        for successor_state, action in state.generatePacmanSuccessors():
            key = self.key(successor_state)
            if key not in closed_states:
                closed_states.add(key)
                v = max(v, self.minimax(successor_state, False, closed_states))
                closed_states.remove(key)

        return v

    def min_value(self, state, closed_states):
        """Minimizing function for ghost's turn."""
        v = float('inf')
        for successor_state, action in state.generateGhostSuccessors(1):
            key = self.key(successor_state)
            if key not in closed_states:
                closed_states.add(key)
                v = min(v, self.minimax(successor_state, True, closed_states))
                closed_states.remove(key)

        return v

    def isTerminal(self, state):
        """Checks if the state is terminal (win or lose)."""
        return state.isWin() or state.isLose()

    def key(self, state):
        """Generates a unique key for the state."""
        return (state.getPacmanPosition(),
                state.getGhostPosition(1),
                state.getFood())
