import numpy as np


def load_input_data(input_data):
    """
    Return input data as numpy array of [edge 1, edge 2]
    """

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    num_nodes = int(firstLine[0])
    num_edges = int(firstLine[1])

    out_array = np.zeros((num_edges, 2))

    for i in range(num_edges):
        line = lines[i + 1]
        parts = line.split()
        out_array[i] = np.array([int(parts[0]), int(parts[1])])

    return out_array, num_nodes


def prepare_output_data(solution_dict, is_provably_optimal=False):
    """
    Return output in specified format.
    """

    if is_provably_optimal:
        optimal = str(1)
    else:
        optimal = str(0)

    output_data = str(solution_dict['num_colours']) + ' ' + optimal + '\n'
    output_data += ' '.join(map(str, solution_dict['solution_array']))

    return output_data

