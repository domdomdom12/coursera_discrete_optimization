import numpy as np
from scipy.spatial.distance import pdist
from scipy.spatial.distance import squareform


def load_input_data(input_data):
    """
    Return input data as numpy array of [x-coordinate, y-coordinate]
    """

    # parse the input
    lines = input_data.split('\n')

    num_nodes = int(lines[0])

    nodes_array = np.zeros((num_nodes, 2))
    for i in range(num_nodes):
        line = lines[i + 1]
        parts = line.split()
        nodes_array[i, :] = np.array([float(parts[0]), float(parts[1])])

    return nodes_array, num_nodes


def make_distance_matrix(nodes_array):
    return squareform(pdist(nodes_array, 'euclidean'))


def prepare_output_data(solution_dict, is_provably_optimal=False):
    """
    Return output in specified format.
    """

    if is_provably_optimal:
        optimal = str(1)
    else:
        optimal = str(0)

    output_data = str(solution_dict['tour_distance']) + ' ' + optimal + '\n'
    output_data += ' '.join(map(str, solution_dict['solution_array']))

    return output_data


