import numpy as np


def load_input_data(input_data):
    """
    Return input data as numpy arrays in a dictionary.
    """

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    num_dropoffs = int(firstLine[0]) - 1
    num_vehicles = int(firstLine[1])
    vehicle_capacity = int(firstLine[2])

    data_dict = {}
    data_dict['num_dropoffs'] = num_dropoffs
    data_dict['num_vehicles'] = num_vehicles
    data_dict['vehicle_capacity'] = vehicle_capacity
    data_dict['warehouse_location'] = np.array([float(lines[1].split()[1]), float(lines[1].split()[2])])

    dropoffs_location_array = np.zeros((num_dropoffs, 2))
    dropoffs_demand_array = np.zeros(num_dropoffs)

    for i in range(num_dropoffs):
        line = lines[i + 2]
        parts = line.split()
        dropoffs_demand_array[i] = parts[0]
        dropoffs_location_array[i, :] = np.array([parts[1], parts[2]])

    data_dict['dropoffs_location_array'] = dropoffs_location_array
    data_dict['dropoffs_demand_array'] = dropoffs_demand_array

    return data_dict


def prepare_output_data(results_dict, is_provably_optimal=False):
    """
    Return output in specified format.
    """

    if is_provably_optimal:
        optimal = str(1)
    else:
        optimal = str(0)

    vehicle_dropoffs_dict = results_dict['vehicle_dropoffs_dict']

    output_data = str(results_dict['route_cost']) + ' ' + optimal + '\n'
    unused_vehicle_count = 0
    for idx, route_list in vehicle_dropoffs_dict.items():
        if route_list != [0, 0]:
            output_data += ' '.join(map(str, route_list)) + '\n'
        else:
            unused_vehicle_count += 1

    for i in range(unused_vehicle_count):
        output_data += '0 0' + '\n'

    return output_data


