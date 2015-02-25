import yaml
import copy

def import_config( process_tuple, process_loading_function, config_file_location, loaded_processes= None):
    new_processes={}
    with open(config_file_location) as f:
        yaml_config= yaml.load(f)
    dependent_load_function= 'loaded_processes' in process_loading_function.__code__.co_varnames
    for process_name,process_parameters in yaml_config.items():
        full_parameters= parse_parameters(process_tuple,process_name,process_parameters)
        new_process= process_tuple(**full_parameters)
        if dependent_load_function: 
            new_processes[process_name]= ( new_process, process_loading_function(new_process, loaded_processes)) 
        else:
            new_processes[process_name]= ( new_process, process_loading_function(new_process)) 
    return new_processes


def parse_parameters( process_tuple, config_name, config_parameters):
    tuple_parameters= process_tuple._fields
    parameters_dict= copy.deepcopy(config_parameters)
    parameters_dict.update({'name':config_name})
    return { tuple_param:parameters_dict.get(tuple_param) for tuple_param in tuple_parameters }
    
