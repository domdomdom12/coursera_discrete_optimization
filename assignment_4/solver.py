#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from assignment_4.data_processing_functions import load_input_data, make_distance_matrix, prepare_output_data
from assignment_4.solving_functions import get_best_greedy_tour

Point = namedtuple("Point", ['x', 'y'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it_trivial(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # build a trivial solution
    # visit the nodes in the order they appear in the file
    solution = range(0, nodeCount)

    # calculate the length of the tour
    obj = length(points[solution[-1]], points[solution[0]])
    for index in range(0, nodeCount-1):
        obj += length(points[solution[index]], points[solution[index+1]])

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def solve_it_greedy(distance_matrix, num_nodes, num_runs=100):

    solution_dict = get_best_greedy_tour(distance_matrix, num_nodes, num_runs=num_runs)

    return solution_dict


def solve_it(input_data):

    nodes_array, num_nodes = load_input_data(input_data)

    distance_matrix = make_distance_matrix(nodes_array)

    if num_nodes < 2000:
        solution_dict = solve_it_greedy(distance_matrix, num_nodes, num_runs=100)
    else:
        solution_dict = solve_it_greedy(distance_matrix, num_nodes, num_runs=1)

    output_data = prepare_output_data(solution_dict, is_provably_optimal=False)

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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

