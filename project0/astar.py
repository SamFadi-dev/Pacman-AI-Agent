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
    """Pacman agent optimized to maximize score through A* search."""

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
        """Given a Pacman game state, returns a list of legal moves
        to maximize score.

        Args:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A list of legal moves.
        """
        closed = set()
        open_queue = PriorityQueue()
        open_queue.push((state, []), 0)
        g_score = {state: 0}

        while not open_queue.isEmpty():
            _, (current, path) = open_queue.pop()

            if current.isWin():
                return path

            current_key = key(current)
            if current_key in closed:
                continue
            closed.add(current_key)

            for successor, action in current.generatePacmanSuccessors():
                successor_key = key(successor)
                if successor_key in closed:
                    continue

                tentative_g_score = g_score[current] + 1
                t_g_score = tentative_g_score
                # Only consider paths that improve the g_score
                if successor not in g_score or t_g_score < g_score[successor]:
                    g_score[successor] = tentative_g_score

                    # Calculate heuristic for the successor
                    pacmanPosition = successor.getPacmanPosition()
                    foodGrid = successor.getFood()
                    heuristics = self.heuristic(pacmanPosition, foodGrid)
                    # f_score considers actual score to favor
                    # states with higher food count
                    score = successor.getScore()
                    f_score = tentative_g_score + heuristics - score

                    new_path = path + [action]
                    open_queue.push((successor, new_path), f_score)

        # No solution
        return []

    def heuristic(self, pacman_pos, food_grid):
        """Heuristic function that considers food clustering.

        Args:
            pacman_pos: Pacman's position in the game.
            food_grid: Grid containing food locations.

        Returns:
            A heuristic cost estimate.
        """
        food_positions = tuple(food_grid.asList())

        # No food left, heuristic is zero
        if not food_positions:
            return 0

        # Calculate maximum distance to any food pellet
        max_food_distance = max(
            manhattanDistance(pacman_pos, food) for food in food_positions
        )

        # Cluster score to favor paths with multiple nearby food dots
        cluster_score = sum(
            1 / (manhattanDistance(pacman_pos, food) + 1)
            for food in food_positions
        )

        # Multiplier to adjust heuristic value based on food count
        multiplier = 1
        if len(food_positions) < 5:
            multiplier = 2
        elif len(food_positions) > 10:
            multiplier = 0.5

        # Combine maximum food distance with a focus on clusters
        heuristic_value = multiplier * max_food_distance - 15 * cluster_score
        return heuristic_value
