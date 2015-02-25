# Defines a state selector
import collections
import yaml
import importlib
import functools

import funtool.lib.config_parse

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


#returns a function, that accepts a state_collection and returns an analysis_collection, to be used as a process
def analysis_selector_process(analysis_selector): 
    analysis_selector_module = importlib.import_module(analysis_selector.selector_module)
    return functools.partial( getattr(analysis_selector_module,analysis_selector.selector_function), analysis_selector )

import_config= functools.partial(funtool.lib.config_parse.import_config, AnalysisSelector, analysis_selector_process)    

