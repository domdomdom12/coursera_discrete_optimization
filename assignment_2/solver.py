#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import namedtuple
Item = namedtuple("Item", ['index', 'value','weight'])

from assignment_2.data_processing_functions import load_input_data, prepare_output_data
from assignment_2.solving_functions import value_per_weight_greedy, dynamic_programming


def solve_it_trivial(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count+1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i-1, int(parts[0]), int(parts[1])))

    # a trivial greedy algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    value = 0
    weight = 0
    taken = [0]*len(items)

    for item in items:
        if weight + item.weight <= capacity:
            taken[item.index] = 1
            value += item.value
            weight += item.weight
    
    # prepare the solution in the specified output format
    output_data = str(value) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, taken))
    return output_data


def solve_it_greedy_value_per_weight(input_array, capacity):

    solution_dict = value_per_weight_greedy(input_array, capacity)

    return solution_dict


def solve_it_dynamic_programming(input_array, capacity):

    solution_dict = dynamic_programming(input_array, capacity)

    return solution_dict


def solve_it(input_data):

    input_array, capacity = load_input_data(input_data)

    if input_array.shape[0] <= 200:
        solution_dict = solve_it_dynamic_programming(input_array, capacity)
        output_data = prepare_output_data(solution_dict, is_provably_optimal=True)
    else:
        solution_dict = solve_it_greedy_value_per_weight(input_array, capacity)
        output_data = prepare_output_data(solution_dict, is_provably_optimal=False)

    #print(solution_dict)

    return output_data


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            data = input_data_file.read()
        print(solve_it(data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')

