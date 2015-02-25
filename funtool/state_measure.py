# A measure performed and recorded on an individual state

import collections
import yaml
import importlib
import functools

import funtool.analysis
import funtool.state_collection
import funtool.logger
import funtool.lib.config_parse
import funtool.lib.general


StateMeasure = collections.namedtuple('StateMeasure',['name','measure_module','measure_function','analysis_selectors','grouping_selectors','parameters'])

# A StateMeasure is used with an AnalysisCollection and a StateCollection to measure each State in the StateCollection
#   Each State will have a new key added to it's measures (or updated if the key already exists)
#   After measuring the state, an AnalysisCollection is returned
#
# name                  a string identifying the measure ( from the key in the YAML measure definition )
# measure_module        a string indicating where the measure_function is defined
# measure_function      a string with the name of the function which measures the state
# analysis_selectors       a list of names of selectors which are run sequentially to update the AnalysisCollection
# grouping_selectors    a list of names of grouping_selectors which are used to create groups in the StateCollection before any analysis is run
# parameters            a dict of parameters passed to the measure 
#
# StateMeasures are run through a loop during the actual analysis ( created in the _wrap_measure function ). The full StateMeasure process returns
# a state_collection

def state_measure_process(state_measure, loaded_processes): #returns a function, that accepts a state_collection, to be used as a process
    return _wrap_measure(individual_state_measure_process(state_measure), state_measure, loaded_processes)

import_config= functools.partial(funtool.lib.config_parse.import_config, StateMeasure, state_measure_process)


def individual_state_measure_process(state_measure): #returns a function that accepts an analysis_collection and a state_collection
    state_measure_module = importlib.import_module(state_measure.measure_module)
    return functools.partial( getattr(state_measure_module,state_measure.measure_function), state_measure )

def _wrap_measure(individual_state_measure_process, state_measure, loaded_processes): 
    """
    Creates a function on a state_collection, which creates analysis_collections for each state in the collection.
    """
    def wrapped_measure(state_collection,overriding_parameters=None,loggers=None):
        if loggers == None:
            loggers = funtool.logger.set_default_loggers()
        if loaded_processes != None :
            if state_measure.grouping_selectors != None:
                for grouping_selector_name in state_measure.grouping_selectors:
                    state_collection= funtool.state_collection.add_grouping(state_collection, grouping_selector_name, loaded_processes) 
            for state in state_collection.states:
                analysis_collection = funtool.analysis.AnalysisCollection(state,None,[])
                if state_measure.analysis_selectors != None:
                    for analysis_selector in state_measure.analysis_selectors:
                        analysis_collection = loaded_processes["analysis_selector"][analysis_selector].process_function(analysis_collection,state_collection)
                if analysis_collection != None:
                    individual_state_measure_process(analysis_collection,state_collection,overriding_parameters)
        return state_collection
    return wrapped_measure
        


def state_and_parameter_measure(state_measure_function):
    """
    Decorator for State Measures that only require the state and parameters

    Saves return value to state.measures with the State Measure's name as the key
    """
    def wrapped_function(state_measure, analysis_collection, state_collection, overriding_parameters=None):
        measure_parameters = get_measure_parameters(state_measure, overriding_parameters)
        measure_value= state_measure_function(analysis_collection.state,measure_parameters)
        analysis_collection.state.measures[state_measure.name] = measure_value
        return analysis_collection
    return wrapped_function

def state_and_parameter_meta(state_measure_function):
    """
    Decorator for State Measures that only require the state and parameters

    Saves return value to state.meta with the State Measure's name as the key
    """
    def wrapped_function(state_measure, analysis_collection, state_collection, overriding_parameters=None):
        measure_parameters = get_measure_parameters(state_measure, overriding_parameters)
        measure_value= state_measure_function(analysis_collection.state,measure_parameters)
        analysis_collection.state.meta[state_measure.name] = measure_value
        return analysis_collection
    return wrapped_function



get_measure_parameters= funtool.lib.general.get_parameters

