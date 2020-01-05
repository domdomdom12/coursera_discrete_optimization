import numpy as np


def traverse_route(route_array, distance_matrix):
    first_index = route_array
    second_index = np.concatenate((route_array[1:], np.array([route_array[0]])))

    return sum(distance_matrix[first_index, second_index])


def greedy_tour(distance_matrix, num_nodes, start_node_index=None,
                second_best_greedy_probability=0):

    # copy distance matrix
    function_distance_matrix = np.copy(distance_matrix)

    # get max from distance matrix + 1
    max_distance_p1 = np.max(function_distance_matrix) + 1

    # initialise solution array
    solution = []

    # if start_node_index isn't given pick one randomly
    if start_node_index is None:
        start_node_index = np.random.randint(num_nodes)

    # initialise current node and append it to the solution
    node_index = start_node_index
    solution.append(node_index)

    # loop until we have no unused indexes left
    while len(solution) < num_nodes:

        # put the used indexes values (the column) up to the max + 1 so we don't visit nodes already visited
        function_distance_matrix[:, node_index].fill(max_distance_p1)

        # choose the next index based on shortest distance to next node, occasionally taking second
        # closest with probability second_best_greedy_probability
        min_indexes = np.argpartition(function_distance_matrix[node_index, :], 2)[:2]
        min_indexes_sorted = min_indexes[np.argsort(function_distance_matrix[node_index, :][min_indexes])]
        if np.random.rand() < second_best_greedy_probability and len(solution) < num_nodes - 2:
            next_index = min_indexes_sorted[1]
        else:
            next_index = min_indexes_sorted[0]

        # append the index to the solution
        solution.append(next_index)

        # set the node index to next index
        node_index = next_index

    return np.array(solution)


def get_best_greedy_tour(distance_matrix, num_nodes, num_runs=100,
                         start_node_index=None,
                         second_best_greedy_probability=0):
    best_solution = greedy_tour(distance_matrix, num_nodes, start_node_index=start_node_index,
                                second_best_greedy_probability=second_best_greedy_probability)
    best_distance = traverse_route(best_solution, distance_matrix)

    for run in range(num_runs - 1):
        solution = greedy_tour(distance_matrix, num_nodes, start_node_index=start_node_index,
                               second_best_greedy_probability=second_best_greedy_probability)
        distance = traverse_route(solution, distance_matrix)
        if distance < best_distance:
            best_solution = solution
            best_distance = distance

    solution_dict = {
        'solution_array': best_solution,
        'tour_distance': best_distance
    }

    return solution_dict



