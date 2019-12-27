import numpy as np


def load_input_data(input_data):
    """
    Return input data as numpy array of [value, weight]
    """

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    out_array = np.zeros((item_count, 2))

    for i in range(item_count):
        line = lines[i + 1]
        parts = line.split()
        out_array[i] = np.array([int(parts[0]), int(parts[1])])

    return out_array, capacity


def prepare_output_data(solution_dict):
    """
    Return output in specified format.
    """

    output_data = str(solution_dict['total_value']) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution_dict['solution_array']))

    return output_data


