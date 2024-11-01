import random
import os

def generate_random_map(width, height):
    if width < 5 or height < 5:
        raise ValueError("Les dimensions doivent être d'au moins 5x5")

    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Créer les bords de la carte avec des murs
    for x in range(width):
        grid[0][x] = "%"
        grid[height - 1][x] = "%"
    for y in range(height):
        grid[y][0] = "%"
        grid[y][width - 1] = "%"

    # Ajouter Pac-Man ('P') à une position aléatoire qui n'est pas un mur
    pac_x, pac_y = random.randint(1, width - 2), random.randint(1, height - 2)
    grid[pac_y][pac_x] = "P"

    # Ajouter un certain nombre de fantômes ('G') à des positions aléatoires
    num_ghosts = 1
    for _ in range(num_ghosts):
        while True:
            ghost_x, ghost_y = random.randint(1, width - 2), random.randint(1, height - 2)
            if grid[ghost_y][ghost_x] == " ":
                grid[ghost_y][ghost_x] = "G"
                break

    # Ajouter des pastilles ('.') dans des positions libres
    num_pellets = random.randint(5, (width * height) // 4)
    for _ in range(num_pellets):
        while True:
            pellet_x, pellet_y = random.randint(1, width - 2), random.randint(1, height - 2)
            if grid[pellet_y][pellet_x] == " ":
                grid[pellet_y][pellet_x] = "."
                break
    # Ajouter des murs intérieurs ('%') à des positions aléatoires
    num_walls = random.randint(5, (width * height) // 4)
    for _ in range(num_walls):
        while True:
            wall_x, wall_y = random.randint(1, width - 2), random.randint(1, height - 2)
            if grid[wall_y][wall_x] == " ":
                grid[wall_y][wall_x] = "%"
                break

    # Convertir la grille en une chaîne de texte
    map_str = "\n".join("".join(row) for row in grid)
    return map_str

def save_map_to_file(map_str, filename):
    with open(filename, 'w') as file:
        file.write(map_str)

# Génération de plusieurs cartes
def generate_and_save_maps(num_maps, width, height, directory="project1/pacman_module/layouts/"):
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    for i in range(num_maps):
        map_str = generate_random_map(width, height)
        filename = os.path.join(directory, f"random_map_{i+1}.lay")
        save_map_to_file(map_str, filename)
        print(f"Carte générée et sauvegardée dans {filename}")

# Exemple : générer 5 cartes aléatoires de 10x10
generate_and_save_maps(num_maps=5, width=10, height=10)
