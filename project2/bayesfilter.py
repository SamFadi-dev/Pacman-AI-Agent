import numpy as np
import math

from pacman_module.game import Agent, Directions, manhattanDistance


class BeliefStateAgent(Agent):
    """Belief state agent.

    Arguments:
        ghost: The type of ghost (as a string).
    """

    def __init__(self, ghost):
        super().__init__()

        self.ghost = ghost

    def compute_legal_moves(slef, x, y, free_cells):
        """Compute the legal moves for the ghost given the walls
        (free cells precomputed).

        Arguments:
            x: The x-coordinate of the ghost.
            y: The y-coordinate of the ghost.
            walls: The W x H grid of walls
                (not used directly here, since free_cells is precomputed).
            free_cells: List of free cells (precomputed).

        Returns:
            A list of legal moves for the ghost.
        """
        moves = []
        # Possible directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        # Get legal moves
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (nx, ny) in free_cells:
                moves.append((nx, ny))

        # If no legal moves, the ghost stays in its current position
        if not moves:
            moves.append((x, y))

        return moves

    def compute_weight(self, distance_to_pacman):
        """Compute the weight factor for the transition matrix.
        Arguments:
            distance_to_pacman: The Manhattan distance to Pacman.
        Returns:
            The weight factor for the transition matrix.
        """
        if self.ghost == "afraid":
            return 1 + distance_to_pacman
        elif self.ghost == "terrified":
            return (distance_to_pacman ** 2)
        elif self.ghost == "fearless":
            return 1
        else:
            print("Invalid ghost type")
            return 1

    def transition_matrix(self, walls, position):
        """Builds the transition matrix

            T_t = P(X_t | X_{t-1})

        given the current Pacman position.

        Arguments:
            walls: The W x H grid of walls.
            position: The current position of Pacman.

        Returns:
            The W x H x W x H transition matrix T_t. The element (i, j, k, l)
            of T_t is the probability P(X_t = (k, l) | X_{t-1} = (i, j)) for
            the ghost to move from (i, j) to (k, l).
        """
        transition_matrix = np.zeros(
            (walls.width, walls.height, walls.width, walls.height))

        # Precompute free cells for efficiency
        free_cells = set(
            (i, j) for i in range(walls.width) for j in range(
                walls.height) if not walls[i][j])

        # Fill the transition matrix
        for i, j in free_cells:
            legal_moves = self.compute_legal_moves(i, j, free_cells)
            total_weight = 0

            for k, l in legal_moves:
                distance_to_pacman = manhattanDistance((k, l), position)
                # Set weight factor based on ghost type
                weight = self.compute_weight(distance_to_pacman)
                transition_matrix[i][j][k][l] = weight
                total_weight += weight

            # Normalize weights (sum to 1)
            if total_weight > 0:
                transition_matrix[i][j] /= total_weight

        return transition_matrix

    def compute_binomial(self, z, n, p):
        """
        Calculate the binomial probability mass function P(z | n, p).

        Arguments:
            z: The number of successes.
            n: The number of trials.
            p: The probability of success in each trial.

        Returns:
            The probability of observing exactly z successes in n trials.
        """
        # Calculate the binomial coefficient (n choose z)
        if z < 0 or z > n:
            return 0
        binomial_coeff = math.factorial(n) // (
            math.factorial(z) * math.factorial(n - z)
            )

        # Calculate the probability using the PMF formula
        probability = binomial_coeff * (p ** z) * ((1 - p) ** (n - z))
        return probability

    def observation_matrix(self, walls, evidence, position):
        """Builds the observation matrix

            O_t = P(e_t | X_t)

        given a noisy ghost distance evidence e_t and the current Pacman
        position.

        Arguments:
            walls: The W x H grid of walls.
            evidence: A noisy ghost distance evidence e_t.
            position: The current position of Pacman.

        Returns:
            The W x H observation matrix O_t.
        """
        # e = ManhattanDistance(Pacman,Ghost) + z − np  z∼Binom(n,p)
        # Binomial distribution parameters
        n = 4
        p = 0.5

        # Initialize the observation matrix
        width, height = walls.width, walls.height
        Observation_matrix = np.zeros((width, height))

        # Fill the observation matrix
        for i in range(width):
            for j in range(height):
                if walls[i][j] is False:
                    distance = manhattanDistance(position, (i, j))
                    # Where z is the noise (make sure it is an integer)
                    z = round(evidence - distance + n * p)
                    # Calculate the probability of observing the evidence
                    # z must be between 0 and n
                    if 0 <= z <= n:
                        Observation_matrix[i][j] = self.compute_binomial(
                            z, n, p)
                    else:
                        Observation_matrix[i][j] = 0

        return Observation_matrix

    def update(self, walls, belief, evidence, position):
        """Updates the previous ghost belief state

            b_{t-1} = P(X_{t-1} | e_{1:t-1})

        given a noisy ghost distance evidence e_t and the current Pacman
        position.

        Arguments:
            walls: The W x H grid of walls.
            belief: The belief state for the previous ghost position b_{t-1}.
            evidence: A noisy ghost distance evidence e_t.
            position: The current position of Pacman.

        Returns:
            The updated ghost belief state b_t as a W x H matrix.
        """

        T = self.transition_matrix(walls, position)
        O = self.observation_matrix(walls, evidence, position)
        updated_belief = np.zeros_like(belief)

        # Debug:
        # print("Initial belief sum:", np.sum(belief))
        # print("Transition matrix sum:", np.sum(T))
        # print("Observation matrix sum:", np.sum(O))

        # b_t = O_t * T_t * b_{t-1} (normalized)
        for i in range(walls.width):
            for j in range(walls.height):
                if walls[i][j]:  # Skip walls
                    continue
                # Sum over all possible (k, l) to compute the updated belief
                belief_sum = 0
                for k in range(walls.width):
                    for l in range(walls.height):
                        belief_sum += T[i, j, k, l] * belief[k, l]

                # Apply the observation likelihood (O[i, j]) to the sum
                updated_belief[i, j] = O[i, j] * belief_sum

        # Normalize to have a probability distribution
        belief_sum_total = np.sum(updated_belief)

        # Add a small epsilon to the sum to avoid division by zero
        epsilon = 1e-10
        final_belief = updated_belief / (belief_sum_total + epsilon)

        return final_belief

    def get_action(self, state):
        """Updates the previous belief states given the current state.

        ! DO NOT MODIFY !

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            The list of updated belief states.
        """

        walls = state.getWalls()
        beliefs = state.getGhostBeliefStates()
        eaten = state.getGhostEaten()
        evidences = state.getGhostNoisyDistances()
        position = state.getPacmanPosition()

        new_beliefs = [None] * len(beliefs)

        for i in range(len(beliefs)):
            if eaten[i]:
                new_beliefs[i] = np.zeros_like(beliefs[i])
            else:
                new_beliefs[i] = self.update(
                    walls,
                    beliefs[i],
                    evidences[i],
                    position,
                )

        return new_beliefs


class PacmanAgent(Agent):
    """Pacman agent that tries to eat ghosts given belief states."""

    def __init__(self):
        super().__init__()

    def get_legal_moves(self, position, walls):
        """
        Compute the legal moves for Pacman given the walls.

        Arguments:
            position: The current position of Pacman as (x, y).
            walls: The W x H grid of walls.

        Returns:
            A list of legal moves as (x, y) tuples.
        """
        x, y = position
        moves = []
        # Possible directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        # Check for legal moves
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < walls.width and 0 <= ny < walls.height:
                # Check if the cell is not a wall
                if walls[nx][ny] is False:
                    moves.append((nx, ny))

        return moves

    def _get_action(self, walls, beliefs, eaten, position):
        """
        Arguments:
            walls: The W x H grid of walls.
            beliefs: The list of current ghost belief states.
            eaten: A list of booleans indicating which ghosts have been eaten.
            position: The current position of Pacman.

        Returns:
            A legal move as defined in `game.Directions`.
        """
        likely_positions = []
        for i, belief in enumerate(beliefs):
            # Skip eaten ghosts
            if eaten[i]:
                continue
            ghost_position = np.unravel_index(np.argmax(belief), belief.shape)
            likely_positions.append(ghost_position)

        # Step 2: Compute legal moves
        legal_moves = self.get_legal_moves(position, walls)

        # Step 3: Choose the best move
        best_move = None
        min_distance = float('inf')
        for move in legal_moves:
            # Compute the distance to the closest likely ghost position
            distance = min(manhattanDistance(move, ghost_pos)
                           for ghost_pos in likely_positions)

            # Get the move with the smallest distance
            if distance < min_distance:
                min_distance = distance
                best_move = move

        # Step 4: Map the best move to a direction
        # Should be a better way to do this
        if best_move:
            dx, dy = best_move[0] - position[0], best_move[1] - position[1]
            direction_mapping = {
                (0, 1): Directions.NORTH,
                (1, 0): Directions.EAST,
                (0, -1): Directions.SOUTH,
                (-1, 0): Directions.WEST,
            }
            return direction_mapping.get((dx, dy), Directions.STOP)

        return Directions.STOP

    def get_action(self, state):
        """Given a Pacman game state, returns a legal move.

        ! DO NOT MODIFY !

        Arguments:
            state: a game state. See API or class `pacman.GameState`.

        Returns:
            A legal move as defined in `game.Directions`.
        """

        return self._get_action(
            state.getWalls(),
            state.getGhostBeliefStates(),
            state.getGhostEaten(),
            state.getPacmanPosition(),
        )
