import numpy as np
from ortools.sat.python import cp_model


def create_node_colour_variables(model, edge_array, num_nodes):
    # fine for now
    num_colours = num_nodes

    node_colour_variables = {}
    for node_index in range(num_nodes):
        node_colour_variables[node_index] = model.NewIntVar(0, num_colours - 1, 'node_%i' % node_index)

    return node_colour_variables, num_colours


def create_node_colour_constraints(model, edge_array, node_colour_variables):
    for edge_index in range(edge_array.shape[0]):
        model.Add(node_colour_variables[edge_array[edge_index, 0]] != node_colour_variables[edge_array[edge_index, 1]])

    return model


def create_colour_used_variables(model, num_colours):
    colour_used_variables = {}
    for colour_index in range(num_colours):
        colour_used_variables[colour_index] = model.NewBoolVar('colour_%i' % colour_index)

    return colour_used_variables


def create_colour_used_constraints(model, node_colour_variables, colour_used_variables, num_nodes, num_colours):
    for colour_index in range(num_colours):
        model.Add(colour_used_variables[colour_index] == min(1, sum([1 for node_index in node_colour_variables.keys()
                                                                     if node_colour_variables[
                                                                         node_index] == colour_index])))

    return model


def create_colour_symmetry_breaking_constraints(model, colour_used_variables, num_colours):
    for colour_index in range(num_colours - 1):
        model.Add(colour_used_variables[colour_index] <= colour_used_variables[colour_index + 1])

    return model


def create_objective(model, node_colour_variables, num_nodes):
    # create objective value variable
    obj_val_var = model.NewIntVar(0, num_nodes - 1, 'num_distinct_colours')

    # add constraint to set the variable
    model.Add(obj_val_var == max([node_colour_variables[node_index] for node_index in range(num_nodes)]))

    model.Minimize(obj_val_var)

    return model


def create_model(edge_array, num_nodes):
    # create model
    model = cp_model.CpModel()

    # create variables
    node_colour_variables, num_colours = create_node_colour_variables(model, edge_array, num_nodes)
    colour_used_variables = create_colour_used_variables(model, num_colours)

    # add constraints
    model = create_node_colour_constraints(model, edge_array, node_colour_variables)
    model = create_colour_used_constraints(model, node_colour_variables, colour_used_variables, num_nodes, num_colours)
    # model = create_colour_symmetry_breaking_constraints(model, edge_array, node_colour_variables, num_nodes)
    model = create_colour_symmetry_breaking_constraints(model, colour_used_variables, num_colours)

    # add objective
    model = create_objective(model, node_colour_variables, num_nodes)

    return model, node_colour_variables  # , colour_used_variables


def solve_model(model, node_colour_variables):
    # solve model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    return model, node_colour_variables, solver, status


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
