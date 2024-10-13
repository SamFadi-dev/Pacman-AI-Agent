from pacman_module.game import *
from pacman_module.util import *


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
    )

class PacmanAgent(Agent):
    """Pacman agent based on depth-first search (DFS)."""

    def __init__(self):
        super().__init__()

        self.moves = None

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move.

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Return:
            A legal move as defined in `game.Directions`.
        """
        if self.moves is None:
            self.moves = self.astar(state)

        if self.moves:
            return self.moves.pop(0)
        else:
            return Directions.STOP

    def astar(self, state):
        """Given a Pacman game state, returns a list of legal moves to solve

        Args:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            a list of legal moves
        """
        closed = set()
        open_queue = PriorityQueue()
        open_queue.push((state, []), 0)
        g_score = {state: 0}
        parent = dict()

        while not open_queue.isEmpty():
            _, (current, path) = open_queue.pop()

            if current.isWin():
                return path

            # Check if the current state is already closed if so skip it
            current_key = key(current)
            if current_key in closed:
                continue
            closed.add(current_key)

            # Generate successors and add them to the open queue
            for successor, action in current.generatePacmanSuccessors():
                # Check if the successor is already closed if so skip it
                successor_key = key(successor)
                if successor_key in closed:
                    continue
                
                # +1 because the cost to move from the current node to the successor is 1 
                # (take me a lot of time to understand this...)
                tentative_g_score = g_score[current] + 1
                
                # Check if the successor is already in the open queue with a better g_score
                if successor not in g_score or tentative_g_score < g_score[successor]:
                    g_score[successor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(successor.getPacmanPosition(), state.getFood())
                    new_path = path + [action]
                    open_queue.push((successor, new_path), f_score)
    
        # No solution
        return []
    
    def reconstruct_path(self, parent, current):
        """Reconstruct the path from the parent dictionary

        Args:
            parent: dictionary containing the parent of each node
            current: the current node

        Returns:
            the total path from the start to the current
        """
        total_path = []
        while parent[current] is not None:
            total_path.insert(0, current)
            current = parent[current]
        return total_path

    def heuristic(self, pacman_pos, food_grid):
        """find the heuristic value for the given pacman position and food grid

        Args:
            pacman_pos: position of pacman
            food_grid: grid of food

        Returns:
            the heuristic value
        """
        food_positions = food_grid.asList() 
        # get the manhattan distance to the closest
        #TODO: find better heuristic
        return min([manhattanDistance(pacman_pos, food) for food in food_positions])
