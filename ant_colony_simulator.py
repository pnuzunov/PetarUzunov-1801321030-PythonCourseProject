import json
import random

# a list containing all possible deltas to the ant's position
random_moves = [
    [0, -1],
    [1, -1],
    [1, 0],
    [1, 1],
    [0, 1],
    [-1, 1],
    [-1, 0],
    [-1, -1]
]

ants = []
board = []
colony_pos = []

# attempts to read file from the given path
def read_file(path):
    with open(path, 'r') as file:
        input = json.load(file)
        return input

# decaying of the pheromones on the board
# called each time all remaining ants make their move
def decay(data):
    for tile in board:
        if tile['tau_a'] >= data['evaporation_factor']:
            tile['tau_a'] -= data['evaporation_factor']
        if tile['tau_b'] >= data['evaporation_factor']:
            tile['tau_b'] -= data['evaporation_factor']

def take_food(data, ant):
    data['food']['quantity'] -= 1
    ant['carries_food'] = True

# ant chooses a random tile to move (if no preference exists)
def move_at_random(x, y):
    random_move = random.randint(0, 7)
    return [x + random_moves[random_move][0], y + random_moves[random_move][1]]

# the actual moving of the ant
def move_ant(data, ant, new_pos):
    old_pos = ant['position']
    index = data['height'] * old_pos[1] + old_pos[0]
    if ant['carries_food']:
        board[index]['tau_b'] = data['delta_tau']
    else:
        board[index]['tau_a'] = data['delta_tau']

    ant['prev_position'] = ant['position']
    ant['position'] = new_pos

# ant chooses its next move
def choose_next_move(data, ant):
    x = ant['position'][0]
    y = ant['position'][1]
    
    # first checks for food, then for pheromones
    for i in range(0, 8):
        # iterating through all possible moves
        check_pos = [x + random_moves[i][0], y + random_moves[i][1]]
        if not check_tile_exists(data, check_pos):
            continue
        if check_tile_has_food(data, ant, check_pos):
            move_ant(data, ant, check_pos)
            return

    for i in range(0, 8):
        check_pos = [x + random_moves[i][0], y + random_moves[i][1]]
        if not check_tile_exists(data, check_pos):
            continue
        if check_tile_preferred(data, ant, check_pos):
            move_ant(data, ant, check_pos)
            return
    
    # if no preference exists, choose a random tile
    new_pos = move_at_random(x, y)
    # the chosen tile cannot be the ant's previous position
    while not check_tile_exists(data, new_pos) or new_pos == ant['prev_position']:
        new_pos = move_at_random(x, y)
    move_ant(data, ant, new_pos)

# checks if the tile is out of bounds
def check_tile_exists(data, pos):
    if pos[0] not in range(0, data['width']) or pos[1] not in range(0, data['height']):
        return False
    return True

# checks if the tile has food
def check_tile_has_food(data, ant, pos):
    if not ant['carries_food']:
        if data['food']['position'] == pos:
            take_food(data, ant)
            return True
    return False

# checks for pheromones
def check_tile_preferred(data, ant, pos):
    # converts the 'x' and 'y' coordinates to the corresponding index of the board list
    index = data['width'] * pos[1] + pos[0]
    if index >= data['width'] * data['height']:
        return False
    if not ant['carries_food']:
    #     if data['food']['position'] == pos:
    #         take_food(data, ant)
    #         return True
        if board[index]['tau_b'] > board[index]['tau_a']:
            return True
    if ant['carries_food']:
        if board[index]['tau_a'] > board[index]['tau_b']:
            return True
    return False

# the output
def print_output():
    print(f'{ants},{board}')

# the function to be run
def run(input_path):

    data = read_file(input_path)

    colony_pos = data['colony_pos']
    for i in range(0, data['num_ants']):
        ants.append({'id': i, 'position': colony_pos, 'prev_position': colony_pos, 'carries_food': False})

    for i in range(0, data['width'] * data['height']):
        board.append({'tau_a': 0.0, 'tau_b': 0.0})

    ants_returned = []
    iterations = 0
    while len(ants) > 0:
        for ant in ants:
            # the ant needs to be back in the colony with food
            if ant['position'] == colony_pos and ant['carries_food']:
                ants.remove(ant)
                ants_returned.append(ant)
            else:
                choose_next_move(data, ant)
        # print_output()
        decay(data)
        iterations += 1
    print(ants_returned)
    print(f'all ants returned after {iterations} round(s).')