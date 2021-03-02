import json
import random


# attempts to read file from the given path
def read_file(path):
    with open(path, 'r') as file:
        input = json.load(file)
        return input

# decaying of the pheromones on the board
# called each time all remaining ants make their move
def decay(board, evaporation_factor):
    for tile in board:
        if tile['tau_a'] >= evaporation_factor:
            tile['tau_a'] -= evaporation_factor
        else:
            tile['tau_a'] = 0.0

        if tile['tau_b'] >= evaporation_factor:
            tile['tau_b'] -= evaporation_factor
        else:
            tile['tau_b'] = 0.0

def take_food(food, delta_food, ant):
    food['quantity'] -= delta_food
    ant['carries_food'] = True

# ant chooses a random tile to move (if no preference exists)
def move_at_random(x, y):
    random_move = random.randint(0, 7)
    return [x + random_moves[random_move][0], y + random_moves[random_move][1]]

# the actual moving of the ant
def move_ant(board, width, delta_tau, ant, new_pos):
    old_pos = ant['position']
    index = width * old_pos[1] + old_pos[0]
    if ant['carries_food']:
        board[index]['tau_b'] = delta_tau
    else:
        board[index]['tau_a'] = delta_tau

    ant['prev_position'] = ant['position']
    ant['position'] = new_pos

# ant chooses its next move
def choose_next_move(data, board, ants, ant):
    x = ant['position'][0]
    y = ant['position'][1]
    width = data['width']
    height = data['height']
    food = data['food']
    delta_food = data['delta_food']
    delta_tau = data['delta_tau']

    # first checks if there's food nearby
    for i in range(0, 8):
        # iterating through all possible moves
        check_pos = [x + random_moves[i][0], y + random_moves[i][1]]
        if not check_tile_exists(width, height, check_pos):
            continue
        if not check_tile_vacant(ants, check_pos):
            continue
        if check_tile_has_food(food, delta_food, ant, check_pos):
            take_food(food, delta_food, ant)
            move_ant(board, width, delta_tau, ant, check_pos)
            return

    # if no food is found, checks nearby tiles' pheromones
    for i in range(0, 8):
        check_pos = [x + random_moves[i][0], y + random_moves[i][1]]
        if not check_tile_exists(width, height, check_pos):
            continue
        if not check_tile_vacant(ants, check_pos):
            continue
        if check_tile_preferred(board, width, height, food, delta_food, ant, check_pos):
            move_ant(board, width, delta_tau, ant, check_pos)
            return
    
    # if no preference exists, choose a random tile
    new_pos = move_at_random(x, y)
    while not check_tile_vacant(ants, new_pos) or not check_tile_exists(width, height, new_pos) or check_tile_was_previous(ant, new_pos):
        new_pos = move_at_random(x, y)
    move_ant(board, width, delta_tau, ant, new_pos)

# checks if the tile is out of bounds
def check_tile_exists(width, height, pos):
    if pos[0] not in range(0, width) or pos[1] not in range(0, height):
        return False
    return True

#checks if the tile was the ant's previous position
def check_tile_was_previous(ant, pos):
    return pos == ant['prev_position']

# checks if an ant is already on the tile
def check_tile_vacant(ants, pos):
    for ant in ants:
        if ant['position'] == pos:
            return False
    return True

# checks if the tile has food
def check_tile_has_food(food, delta_food, ant, pos):
    if not ant['carries_food']:
        if food['position'] == pos:
            return True
    return False

# checks for pheromones
def check_tile_preferred(board, width, height, food, delta_food, ant, pos):
    # converts the 'x' and 'y' coordinates to the corresponding index of the board list
    index = width * pos[1] + pos[0]
    if index >= width * height:
        return False

    if not check_tile_has_food(food, delta_food, ant, pos) and check_tile_was_previous(ant, pos):
        return False

    if not ant['carries_food']:
        if board[index]['tau_b'] > board[index]['tau_a']:
            return True
    if ant['carries_food']:
        if board[index]['tau_a'] > board[index]['tau_b']:
            return True
    return False

# the output
def print_output(ants, board):
    list_ants = []

    # copies ants to a new list so the 'prev_position' key can be removed
    for ant in ants:
        list_ants.append(ant.copy())
    # for ant in list_ants:
    #     del ant['prev_position']

    # connects the new ants list with the board list
    dict_for_print = dict.fromkeys(('ants', 'board'))
    dict_for_print['ants'] = list_ants
    # dict_for_print['board'] = board
    print(json.dumps(dict_for_print))

# the function to be run
def run(input_path):

    data = read_file(input_path)

    # a list containing all possible deltas to the ant's position
    global random_moves
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
    evaporation_factor = data['evaporation_factor']

    for i in range(0, data['num_ants']):
        # also adds a 'prev_position' key so the ants can remember their position in the previous iteration
        ants.append({'id': i, 'position': data['colony_pos'], 'prev_position': data['colony_pos'], 'carries_food': False})

    for i in range(0, data['width'] * data['height']):
        board.append({'tau_a': 0.0, 'tau_b': 0.0})

    iterations = 0
    while data['food']['quantity'] > 0:
        for ant in ants:
            if not ant['position'] == data['colony_pos'] or not ant['carries_food']:
                choose_next_move(data, board, ants, ant)
            else:
                ant['carries_food'] = False
        decay(board, evaporation_factor)
        iterations += 1
        # print_output(ants, board)

    # while not all_ants_returned:


    print_output(ants, board)
    print(f'all ants returned after {iterations} round(s).')