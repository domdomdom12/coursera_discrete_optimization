import numpy as np
from ortools.sat.python import cp_model


def greedy_colouring(edge_array):
    def color_nodes(graph):
        color_map = {}
        # Consider nodes in descending degree
        for node in sorted(graph, key=lambda x: len(graph[x]), reverse=True):
            neighbor_colors = set(color_map.get(neigh) for neigh in graph[node])
            color_map[node] = next(
                color for color in range(len(graph)) if color not in neighbor_colors
            )
        return color_map

    node_neighbour_dict = {}

    for edge_index in range(edge_array.shape[0]):
        v0, v1 = int(edge_array[edge_index, 0]), int(edge_array[edge_index, 1])
        if v0 not in node_neighbour_dict:
            node_neighbour_dict[v0] = []
        node_neighbour_dict[v0].append(v1)
        if v1 not in node_neighbour_dict:
            node_neighbour_dict[v1] = []
        node_neighbour_dict[v1].append(v0)

    solution_dict = color_nodes(node_neighbour_dict)

    solution_array = np.zeros(int(edge_array.max() + 1))
    obj_val = 0
    for i in range(int(edge_array.max() + 1)):
        colour = solution_dict[i]
        solution_array[i] = colour
        obj_val = max(obj_val, colour)

    out_dict = {
        'solution_array': solution_array.astype(int),
        'num_colours': obj_val + 1
    }

    return out_dict


def order_nodes_by_order_desc(edge_array):
    node_order_dict = {}

    for node_index in range(int(edge_array.max()) + 1):
        count_node_edges = (edge_array == node_index).sum()
        node_order_dict[node_index] = count_node_edges

    node_by_order_desc = [tup[0] for tup in sorted(node_order_dict.items(), key=lambda x: x[1], reverse=True)]

    return node_by_order_desc


def order_nodes_by_neighbours_order_descending(edge_array):
    node_neighbour_dict = {}

    for edge_index in range(edge_array.shape[0]):
        v0, v1 = int(edge_array[edge_index, 0]), int(edge_array[edge_index, 1])
        if v0 not in node_neighbour_dict:
            node_neighbour_dict[v0] = []
        node_neighbour_dict[v0].append(v1)
        if v1 not in node_neighbour_dict:
            node_neighbour_dict[v1] = []
        node_neighbour_dict[v1].append(v0)

    node_neighbours_order_dict = {}
    for node, neighbours in node_neighbour_dict.items():
        node_neighbours_neighbors = 0
        for neighbour in neighbours:
            node_neighbours_neighbors += len(node_neighbour_dict[neighbour])
        node_neighbours_order_dict[node] = node_neighbours_neighbors

    out_list = [tup[0] for tup in sorted(node_neighbours_order_dict.items(), key=lambda x: x[1], reverse=True)]

    return out_list


def create_node_colour_variables(model, edge_array, num_nodes, num_colours=None):
    # fine for now
    if num_colours is None:
        num_colours = num_nodes

    node_colour_variables = {}
    for counter, node_index in enumerate(order_nodes_by_neighbours_order_descending(edge_array)):
        node_colour_variables[node_index] = model.NewIntVar(0, num_colours - 1, 'node_%i' % counter)

    return node_colour_variables, num_colours


def create_node_colour_constraints(model, edge_array, node_colour_variables):
    for edge_index in range(edge_array.shape[0]):
        model.Add(node_colour_variables[edge_array[edge_index, 0]] != node_colour_variables[edge_array[edge_index, 1]])

    return model


def create_node_colour_bool_variables(model, edge_array, num_nodes, num_colours=None):
    # fine for now
    if num_colours is None:
        num_colours = num_nodes

    node_colour_bool_variables = {}
    for counter, node_index in enumerate(order_nodes_by_neighbours_order_descending(edge_array)):
        for colour_index in range(num_colours):
            node_colour_bool_variables[(node_index, colour_index)] = \
                model.NewBoolVar('node_%i_colour_%i' % (counter, colour_index))

    return node_colour_bool_variables


def create_node_colour_bool_constraints(model, node_colour_bool_variables,
                                        node_colour_variables, num_nodes, num_colours):
    for node_index in range(num_nodes):
        for colour_index in range(num_colours):
            model.Add(node_colour_variables[node_index] == colour_index). \
                OnlyEnforceIf(node_colour_bool_variables[(node_index, colour_index)])
            model.Add(node_colour_variables[node_index] != colour_index). \
                OnlyEnforceIf(node_colour_bool_variables[(node_index, colour_index)].Not())

    return model


def create_colour_used_variables(model, num_colours):
    colour_used_variables = {}
    for colour_index in range(num_colours):
        colour_used_variables[colour_index] = model.NewBoolVar('colour_%i' % colour_index)

    return colour_used_variables


def create_colour_used_constraints(model, node_colour_bool_variables, colour_used_variables, num_nodes, num_colours):
    for colour_index in range(num_colours):
        model.AddMaxEquality(colour_used_variables[colour_index],
                             [node_colour_bool_variables[(node_index, colour_index)]
                              for node_index in range(num_nodes)])

    return model


def create_colour_symmetry_breaking_constraints(model, colour_used_variables, num_colours):
    for colour_index in range(num_colours - 1):
        model.Add(colour_used_variables[colour_index] >= colour_used_variables[colour_index + 1])

    return model


def create_objective(model, colour_used_variables, num_colours):
    # create objective value variable
    obj_val_var = model.NewIntVar(0, num_colours - 1, 'num_distinct_colours')

    # add constraint to set the variable
    model.Add(obj_val_var == sum([colour_used_variables[colour_index] for colour_index in range(num_colours)]))

    model.Minimize(obj_val_var)

    return model, obj_val_var


def create_model(edge_array, num_nodes, max_obj=None):
    # create model
    model = cp_model.CpModel()

    # create variables
    node_colour_variables, num_colours = create_node_colour_variables(model, edge_array, num_nodes, num_colours=max_obj)
    node_colour_bool_variables = create_node_colour_bool_variables(model, edge_array, num_nodes, num_colours=max_obj)
    colour_used_variables = create_colour_used_variables(model, num_colours)

    # add constraints
    model = create_node_colour_bool_constraints(model, node_colour_bool_variables, node_colour_variables,
                                                num_nodes, num_colours)
    model = create_node_colour_constraints(model, edge_array, node_colour_variables)
    model = create_colour_used_constraints(model, node_colour_bool_variables, colour_used_variables, num_nodes,
                                           num_colours)
    model = create_colour_symmetry_breaking_constraints(model, colour_used_variables, num_colours)

    # add objective
    model, obj_val_variable = create_objective(model, colour_used_variables, num_colours)

    # if we have a known max value for the objective, restrict to be lower than this
    if max_obj is not None:
        model.Add(obj_val_variable <= max_obj)

    model.AddDecisionStrategy([node_colour_variables[node_index]
                               for node_index in order_nodes_by_neighbours_order_descending(edge_array)],
                              cp_model.CHOOSE_FIRST, cp_model.SELECT_MIN_VALUE)

    return model, node_colour_variables, node_colour_bool_variables, colour_used_variables, obj_val_variable


def solve_model(model, max_solve_time=10):
    # solve model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = max_solve_time
    solver.parameters.search_branching = cp_model.FIXED_SEARCH
    solver.parameters.num_search_workers = 16
    solver.parameters.randomize_search = True
    status = solver.Solve(model)

    return model, solver, status


def print_results(model, variables, obj_val_variable, solver):
    max_obj = 0

    for node_index, node_var in variables.items():
        val = solver.Value(node_var)
        max_obj = max(max_obj, val)
        print('Node ' + str(node_index) + ': ' + str(val))

    print('Objective: ' + str(solver.Value(obj_val_variable)))


def get_solution_dict(variables, solver, num_nodes):
    max_obj = 0

    solution_array = np.zeros(num_nodes)

    for node_index, node_var in variables.items():
        val = solver.Value(node_var)
        solution_array[node_index] = val
        max_obj = max(max_obj, val)

    solution_dict = {
        'solution_array': solution_array.astype(int),
        'num_colours': max_obj + 1
    }

    return solution_dict
