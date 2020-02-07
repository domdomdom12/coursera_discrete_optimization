import numpy as np
from time import ctime
import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from pyomo.core.base import Constraint as pyo_constraint
from pyomo.core.base import Var as pyo_vars
from assignment_5.data_processing_functions import create_facility_customer_dist_matrix


def greedy_solution(data_dict, facility_customer_dist_matrix=None):
    if facility_customer_dist_matrix is None:
        facility_customer_dist_matrix = create_facility_customer_dist_matrix(data_dict)

    facility_cost_array = data_dict['facility_cost_array']
    facility_capacity_array = data_dict['facility_capacity_array']
    customer_demand_array = data_dict['customer_demand_array']

    num_facilities = len(facility_capacity_array)

    facility_customers = {}
    fixed_costs = 0
    transport_costs = 0

    facility_remaining_capacity = {counter: facility_capacity_array[counter]
                                   for counter in range(num_facilities)}

    customer_ordering = np.argsort(np.min(facility_customer_dist_matrix, axis=0))

    for customer in customer_ordering:
        closest_facility_indexes = np.argsort(facility_customer_dist_matrix[:, customer])
        customer_demand = customer_demand_array[customer]
        customer_allocated = False
        counter = 0
        # print('customer: ' + str(customer))
        # print('customer_demand: ' + str(customer_demand))
        while not customer_allocated:
            facility = closest_facility_indexes[counter]
            # print('facility: ' + str(facility))
            # print('facility capacity: ' +str(facility_remaining_capacity[facility]))
            if facility in facility_customers.keys():
                if facility_remaining_capacity[facility] >= customer_demand:
                    facility_customers[facility].append(customer)
                    facility_remaining_capacity[facility] -= customer_demand
                    transport_costs += facility_customer_dist_matrix[facility, customer]
                    customer_allocated = True
                    # print('used facility ' + str(facility))
                else:
                    counter += 1
            else:
                facility_customers[facility] = [customer]
                facility_remaining_capacity[facility] -= customer_demand
                fixed_costs += facility_cost_array[facility]
                transport_costs += facility_customer_dist_matrix[facility, customer]
                customer_allocated = True
                # print('used facility ' + str(facility))
        # print(' ')

    out_dict = {}
    out_dict['facility_customers'] = facility_customers
    out_dict['fixed_costs'] = fixed_costs
    out_dict['transport_costs'] = transport_costs
    out_dict['objective_value'] = fixed_costs + transport_costs
    out_dict['is_optimal'] = False

    return out_dict


def objective_function(model):
    return sum(model.fixed_costs[f] * model.x[f] for f in model.F) \
           + sum(sum(model.transport_costs[f, c] * model.y[f, c] for f in model.F) for c in model.C)


def constraint_open_facilities(model, f, c):
    return model.y[f, c] <= model.x[f]


def constraint_customer_assigned(model, c):
    return sum(model.y[f, c] for f in model.F) == 1


def constraint_capacity(model, f):
    return sum(model.demands[c] * model.y[f, c] for c in model.C) <= model.capacities[f]


def build_model(data_dict, facility_customer_dist_matrix=None):
    if facility_customer_dist_matrix is None:
        facility_customer_dist_matrix = create_facility_customer_dist_matrix(data_dict)

    facility_cost_array = data_dict['facility_cost_array']
    facility_capacity_array = data_dict['facility_capacity_array']
    customer_demand_array = data_dict['customer_demand_array']

    model = pyo.ConcreteModel()

    model.F = pyo.Set(initialize=[f for f in range(len(facility_cost_array))])
    model.C = pyo.Set(initialize=[c for c in range(len(customer_demand_array))])

    model.fixed_costs = pyo.Param(model.F, within=pyo.NonNegativeReals,
                                  initialize={counter: element for counter, element in
                                              enumerate(facility_cost_array)}, default=0.0)
    model.transport_costs = pyo.Param(model.F, model.C, within=pyo.NonNegativeReals,
                                      initialize={
                                          (counter_1, counter_2): facility_customer_dist_matrix[counter_1, counter_2]
                                          for counter_1 in range(len(facility_cost_array))
                                          for counter_2 in range(len(customer_demand_array))},
                                      default=0.0)
    model.demands = pyo.Param(model.C, within=pyo.NonNegativeReals,
                              initialize={counter: element for counter, element in
                                          enumerate(customer_demand_array)}, default=0.0)
    model.capacities = pyo.Param(model.F, within=pyo.NonNegativeReals,
                                 initialize={counter: element for counter, element in
                                             enumerate(facility_capacity_array)}, default=0.0)

    model.x = pyo.Var(model.F, within=pyo.Binary)
    model.y = pyo.Var(model.F, model.C, within=pyo.Binary)

    model.objective_function = pyo.Objective(rule=objective_function, sense=pyo.minimize)
    model.constraint_open_facilities = pyo.Constraint(model.F, model.C, rule=constraint_open_facilities)
    model.constraint_customer_assigned = pyo.Constraint(model.C, rule=constraint_customer_assigned)
    model.constraint_capacity = pyo.Constraint(model.F, rule=constraint_capacity)

    return model


def solve_model_milp(model, solver_name, solver_path, timeout_time=120, ratio_gap=0.01, show_working=True):
    print('Run start time: ' + str(ctime()))

    # Use CPLEX on the NEOS server
    if solver_name == 'cplex':
        manager = pyo.SolverManagerFactory('neos')
        opt_settings = SolverFactory(solver_name)
        opt_settings.set_options('mipgap=' + str(ratio_gap))
        opt_settings.set_options('timelimit=' + str(timeout_time))
        opt_settings.set_options('mipdisplay=' + str(3))
        opt_settings.set_options('nodefile=' + str(2))
        opt_settings.set_options('treememory=' + str(10000))
        results = manager.solve(model, opt=opt_settings, keepfiles=True)

    elif solver_name == 'cbc':
        opt_settings = SolverFactory(solver_name, executable=solver_path)
        opt_settings.set_options('sec=' + str(timeout_time))
        opt_settings.set_options('ratioGap=' + str(ratio_gap))
        results = opt_settings.solve(model, tee=show_working)

    else:
        raise ValueError(f'Solver {solver_name} not supported')

    print('Run finish time: ' + str(ctime()))

    return model, results


def get_results_dict(model, results, data_dict, facility_customer_dist_matrix=None):
    if facility_customer_dist_matrix is None:
        facility_customer_dist_matrix = create_facility_customer_dist_matrix(data_dict)

    out_dict = {'facility_customers': {}}
    fixed_costs = 0
    transport_costs = 0

    for tup, val in model.y.get_values().items():
        facility, customer = tup[0], tup[1]
        if val == 1:
            if facility not in out_dict['facility_customers']:
                out_dict['facility_customers'][facility] = [customer]
                fixed_costs += data_dict['facility_cost_array'][facility]
            else:
                out_dict['facility_customers'][facility].append(customer)
            transport_costs += facility_customer_dist_matrix[facility, customer]

    if str(list(results['Solver'])[0]['Termination condition']) == 'optimal':
        is_optimal = True
    else:
        is_optimal = False

    out_dict['fixed_costs'] = fixed_costs
    out_dict['transport_costs'] = transport_costs
    out_dict['objective_value'] = fixed_costs + transport_costs
    out_dict['is_optimal'] = is_optimal

    return out_dict

