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
        # Cache for the heuristic function
        # Idk if I can put it here
        self.heuristic_cache = {}

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

                # +1 because the cost to move from the current node to the
                # successor is 1 (take me a lot of time to understand this...)
                tentative_g_score = g_score[current] + 1

                # Check if the successor is already
                # in the open queue with a better g_score
                succ = successor
                if succ not in g_score or tentative_g_score < g_score[succ]:
                    g_score[successor] = tentative_g_score
                    pacmanPosition = successor.getPacmanPosition()
                    foods = successor.getFood()
                    heuristics = self.heuristic(pacmanPosition, foods)
                    f_score = tentative_g_score + heuristics
                    new_path = path + [action]
                    open_queue.push((successor, new_path), f_score)

        # No solution
        return []

    def heuristic(self, pacman_pos, food_grid):
        # Get the food positions
        food_positions = tuple(food_grid.asList())

        # Get in cache if possible
        if (pacman_pos, food_positions) in self.heuristic_cache:
            return self.heuristic_cache[(pacman_pos, food_positions)]

        # If not cached, compute the heuristic
        if not food_positions:
            heuristic_value = 0
        else:
            # Calculate the nearest food distance
            nearest_food = min(
                manhattanDistance(pacman_pos, food) for food in food_positions
            )

            # Approximate the MST cost by summing
            # distances between nearest food points
            mst_cost = 0
            unvisited = set(food_positions)
            current_pos = food_positions[0]
            unvisited.remove(current_pos)

            while unvisited:
                # Find the nearest unvisited food position from current_pos
                next_food = min(
                    unvisited, key=lambda food: manhattanDistance(
                        current_pos, food
                        )
                    )
                # Add the distance to mst_cost and move to next_food
                mst_cost += manhattanDistance(current_pos, next_food)
                current_pos = next_food
                unvisited.remove(current_pos)

            heuristic_value = nearest_food + mst_cost

        # Cache the computed heuristic value
        self.heuristic_cache[(pacman_pos, food_positions)] = heuristic_value
        return heuristic_value
