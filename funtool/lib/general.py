import copy

def get_parameters(process_tuple, overriding_parameters):
    tuple_parameters= copy.deepcopy(process_tuple.parameters)
    if overriding_parameters != None:
        if tuple_parameters is None:
            tuple_parameters = {}
        for param, val in overriding_parameters.items():
            tuple_parameters[param] = val
    return tuple_parameters
