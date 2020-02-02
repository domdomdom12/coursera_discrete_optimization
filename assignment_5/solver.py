#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
from assignment_5.data_processing_functions import load_input_data, prepare_output_data
from assignment_5.solving_functions import greedy_solution, build_model,  solve_model_milp, get_results_dict

Point = namedtuple("Point", ['x', 'y'])
Facility = namedtuple("Facility", ['index', 'setup_cost', 'capacity', 'location'])
Customer = namedtuple("Customer", ['index', 'demand', 'location'])

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it_trivial(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])
    
    facilities = []
    for i in range(1, facility_count+1):
        parts = lines[i].split()
        facilities.append(Facility(i-1, float(parts[0]), int(parts[1]), Point(float(parts[2]), float(parts[3])) ))

    customers = []
    for i in range(facility_count+1, facility_count+1+customer_count):
        parts = lines[i].split()
        customers.append(Customer(i-1-facility_count, int(parts[0]), Point(float(parts[1]), float(parts[2]))))

    # build a trivial solution
    # pack the facilities one by one until all the customers are served
    solution = [-1]*len(customers)
    capacity_remaining = [f.capacity for f in facilities]

    facility_index = 0
    for customer in customers:
        if capacity_remaining[facility_index] >= customer.demand:
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand
        else:
            facility_index += 1
            assert capacity_remaining[facility_index] >= customer.demand
            solution[customer.index] = facility_index
            capacity_remaining[facility_index] -= customer.demand

    used = [0]*len(facilities)
    for facility_index in solution:
        used[facility_index] = 1

    # calculate the cost of the solution
    obj = sum([f.setup_cost*used[f.index] for f in facilities])
    for customer in customers:
        obj += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data


def solve_it_greedy(data_dict):

    results_dict = greedy_solution(data_dict)

    output_data = prepare_output_data(data_dict, results_dict, is_provably_optimal=results_dict['is_optimal'])

    return output_data

def solve_it_mip(data_dict):

    model_instance = build_model(data_dict)

    model_instance, results_instance = solve_model_milp(model_instance,
                                                        'cplex','neos', #'cbc',
                                                        #r'C:\repos\coursera_discrete_optimization\solvers\cbc\bin\cbc.exe',
                                                        timeout_time=300, ratio_gap=0, show_working=True)

    results_dict = get_results_dict(model_instance, results_instance, data_dict)

    output_data = prepare_output_data(data_dict, results_dict, is_provably_optimal=results_dict['is_optimal'])

    return output_data


def solve_it(input_data):

    data_dict = load_input_data(input_data)

    if len(data_dict['facility_cost_array']) >= 500:
        output_data = solve_it_greedy(data_dict)
    else:
        output_data = solve_it_mip(data_dict)

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
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)')

