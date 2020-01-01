#!/usr/bin/python
# -*- coding: utf-8 -*-

from assignment_3.data_processing_functions import load_input_data, prepare_output_data
from assignment_3.solving_functions import create_model, solve_model, get_solution_dict

def solve_it_trivial(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []
    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    # build a trivial solution
    # every node has its own color
    solution = range(0, node_count)

    # prepare the solution in the specified output format
    output_data = str(node_count) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def solve_it_cp(edge_array, num_nodes):

    model, nc_vars, ncb_vars, cu_vars, obj_val_var = create_model(edge_array, num_nodes)

    model, solv, stat = solve_model(model, max_solve_time=120)

    solution_dict = get_solution_dict(nc_vars, solv, num_nodes)

    return solution_dict


def solve_it(input_data):

    edge_array, num_nodes = load_input_data(input_data)

    solution_dict = solve_it_cp(edge_array, num_nodes)

    output_data = prepare_output_data(solution_dict, is_provably_optimal=False)

    # print(solution_dict)

    return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

