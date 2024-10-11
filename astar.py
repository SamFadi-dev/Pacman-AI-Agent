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
        # ...
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

        closed = set()
        open_queue = PriorityQueue()
        open_queue.push((state, []), 0)
        g_score = {state: 0}
        parent = dict()

        while not open_queue.isEmpty():
            _, (current, path) = open_queue.pop()

            if current.isWin():
                return path

            # Check if the current state is already closed
            current_key = key(current)
            if current_key in closed:
                continue
            closed.add(current_key)

            # Generate successors 
            for successor, action in current.generatePacmanSuccessors():
                # Check if the successor is already closed
                successor_key = key(successor)
                if successor_key in closed:
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if successor not in g_score or tentative_g_score < g_score[successor]:
                    g_score[successor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(successor.getPacmanPosition(), state.getFood())
                    
                    new_path = path + [action]  # Add the action to the current path
                    open_queue.push((successor, new_path), f_score)
                    
        # No solution
        return []
    
    def reconstruct_path(self, parent, current):
        total_path = []
        while parent[current] is not None:
            total_path.insert(0, current)
            current = parent[current]
        return total_path

    def heuristic(self, point1, food_grid):
        food_positions = food_grid.asList() 
        # get the manhattan distance to the closest
        return min([manhattanDistance(point1, food) for food in food_positions])
