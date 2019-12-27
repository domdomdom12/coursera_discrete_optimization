import numpy as np


def value_per_weight_greedy(input_array, capacity):
    """
    Greedy algorithm to choose items based on first their value density, then their value.
    """

    # get an array of value per weight, with a small addition based on value to prioritise
    # high value items if the vpw is the same
    vpw_array = input_array[:, 0] / input_array[:, 1] + input_array[:, 0] / (max(input_array[:, 0]) * 10000)
    vpw_array_argsort = np.argsort(vpw_array)[::-1]
    num_items = input_array.shape[0]

    total_value = 0
    total_weight = 0
    solution_array = np.zeros(num_items)

    counter = 0
    while total_weight < capacity:
        if counter >= num_items:
            break
        index = vpw_array_argsort[counter]
        weight = input_array[index, 1]
        value = input_array[index, 0]
        counter += 1
        if total_weight + weight <= capacity:
            total_value += value
            total_weight += weight
            solution_array[index] = 1

    out_dict = {
        'solution_array': solution_array.astype(int),
        'total_value': int(total_value),
        'total_weight': int(total_weight)
    }

    return out_dict


def dynamic_programming_helper(input_array, capacity, item_num, memorisation_dict={}):
    """
    Implement a dynamic programming approach with memorisation - helper function.
    """

    value = input_array[item_num - 1, 0]
    weight = input_array[item_num - 1, 1]

    if (capacity, item_num) in memorisation_dict.keys():
        return memorisation_dict[(capacity, item_num)]

    # if there are no items we want to return 0
    if item_num == 0:
        output = 0

    else:
        # check if we have the answer stored for the same capacity and one less item
        if (capacity, item_num - 1) in memorisation_dict.keys():
            item_not_added = memorisation_dict[(capacity, item_num - 1)]
        else:
            item_not_added, memorisation_dict = dynamic_programming_helper(input_array, capacity,
                                                                           item_num - 1,
                                                                           memorisation_dict=memorisation_dict)

        # get the answer if the item is added
        if weight <= capacity:
            if (capacity - weight, item_num - 1) in memorisation_dict.keys():
                item_added = memorisation_dict[(capacity - weight, item_num - 1)]
            else:
                item_added, memorisation_dict = dynamic_programming_helper(input_array, capacity - weight,
                                                                           item_num - 1,
                                                                           memorisation_dict=memorisation_dict)
                item_added += value

                # choose max of answers with the item either added or not
            output = max(item_not_added, item_added)

        else:
            output = item_not_added

    # add the answer to our memorisation dictionary
    memorisation_dict[(capacity, item_num)] = output

    return int(output), memorisation_dict


def get_solution_from_memorisation_dict(input_array, memorisation_dict):
    num_items = max([i[1] for i in memorisation_dict.keys()])

    out_array = np.zeros(num_items)
    total_weight = 0

    capacity = max([i[0] for i in memorisation_dict.keys()])
    for item in range(num_items, 0, -1):
        if memorisation_dict[(capacity, item)] > memorisation_dict[(capacity, item - 1)]:
            out_array[item - 1] = 1
            weight = input_array[item - 1, 1]
            capacity -= weight
            total_weight += weight

    return out_array, total_weight


def dynamic_programming(input_array, capacity):
    num_items = input_array.shape[0]

    total_value, memorisation_dict = dynamic_programming_helper(input_array, capacity, num_items)

    solution_array, total_weight = get_solution_from_memorisation_dict(input_array, memorisation_dict)

    out_dict = {
        'solution_array': solution_array.astype(int),
        'total_value': int(total_value),
        'total_weight': int(total_weight)
    }

    return out_dict
