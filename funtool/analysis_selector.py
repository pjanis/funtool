# Defines a state selector
import collections
import yaml
import importlib
import functools

AnalysisSelector = collections.namedtuple('AnalysisSelector',['selector_module','selector_function','parameters'])

# A state selector is one which selects one or more states based on a particular state
#    
# selector_module           the module where the selector function is defined 
# selector_function         a function used to create the selection
# parameters                a dict of parameters for the selector function
#
# For example: One state selector may find all the states with the same user id as a given state
#
# Another example: A state selector to find the next state based on on time stamp


def import_config(config_file_location):
    new_analysis_selectors={}
    with open(config_file_location) as f:
        yaml_config= yaml.load(f)
    for analysis_selector_name,analysis_selector_parameters in yaml_config.items():
        new_analysis_selector= AnalysisSelector(**analysis_selector_parameters)
        new_analysis_selectors[analysis_selector_name]= (new_analysis_selector, analysis_selector_process(new_analysis_selector)) 
            # for ** explination https://docs.python.org/2/tutorial/controlflow.html#tut-unpacking-arguments

    return new_analysis_selectors

#returns a function, that accepts a state_collection and returns an analysis_collection, to be used as a process
def analysis_selector_process(analysis_selector): 
    analysis_selector_module = importlib.import_module(analysis_selector.selector_module)
    return functools.partial( getattr(analysis_selector_module,analysis_selector.selector_function), analysis_selector )
    

