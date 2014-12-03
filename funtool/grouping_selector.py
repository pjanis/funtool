# Defines Grouping Selector 
import collections
import yaml
import importlib
import functools



GroupingSelector = collections.namedtuple('GroupingSelector',['grouping_selector_name','selector_module','selector_function','parameters'])

# A grouping selector is used to create a set of groups. This differs from a state selector which may create
#   a set of states. A group selector does not need to place each state in a collection into a group, but 
#   it often will (i.e. grouping saves by user_id ). 

# grouping_selector_name    The name of the selector ( taken from the YAML definition)
# selector_module           the module where the selector function is defined 
# selector_function         a function used to create the selection
# parameters                a dict of parameters for the selector function
#
# A grouping selector process returns a state collection with the state_collections groups_dict updated
#  AND WITH groups_dict updated in each state !!!


def import_config(config_file_location):
    new_grouping_selectors={}
    with open(config_file_location) as f:
        yaml_config= yaml.load(f)
    for grouping_selector_name,grouping_selector_parameters in yaml_config.items():
        new_grouping_selector= GroupingSelector(grouping_selector_name= grouping_selector_name, **grouping_selector_parameters)
        new_grouping_selectors[grouping_selector_name]= (new_grouping_selector, grouping_selector_process(new_grouping_selector)) 
            # for ** explination https://docs.python.org/2/tutorial/controlflow.html#tut-unpacking-arguments

    return new_grouping_selectors


def grouping_selector_process(grouping_selector): #returns a function, that accepts a state_collection, to be used as a process
    grouping_selector_module = importlib.import_module(grouping_selector.selector_module)
    return functools.partial( getattr(grouping_selector_module,grouping_selector.selector_function), grouping_selector )
    

