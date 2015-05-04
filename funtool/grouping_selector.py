# Defines Grouping Selector 
import collections
import yaml
import importlib
import functools

import funtool.lib.config_parse
import funtool.lib.general

GroupingSelector = collections.namedtuple('GroupingSelector',['name','selector_module','selector_function','parameters'])

# A grouping selector is used to create a set of groups. This differs from a state selector which may create
#   a set of states. A group selector does not need to place each state in a collection into a group, but 
#   it often will (i.e. grouping saves by user_id ). 

# name                      The name of the selector ( taken from the YAML definition)
# selector_module           the module where the selector function is defined 
# selector_function         a function used to create the selection
# parameters                a dict of parameters for the selector function
#
# A grouping selector process returns a state collection with the state_collections groupings updated
#  AND WITH groupings updated in each state !!!


def grouping_selector_process(grouping_selector): #returns a function, that accepts a state_collection, to be used as a process
    grouping_selector_module = importlib.import_module(grouping_selector.selector_module)
    return functools.partial( getattr(grouping_selector_module,grouping_selector.selector_function), grouping_selector )

import_config= functools.partial(funtool.lib.config_parse.import_config, GroupingSelector, grouping_selector_process)
    

def add_groups_to_grouping(state_collection, grouping_name, groups):
    current_groups= state_collection.groupings.get(grouping_name)
    if current_groups is None:
        state_collection.groupings[grouping_name]= groups
    else:
        state_collection.groupings[grouping_name]+= groups
    return state_collection

get_selector_parameters= funtool.lib.general.get_parameters
