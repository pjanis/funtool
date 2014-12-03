# A measure performed and recorded on an individual state

import collections
import yaml
import importlib
import functools

import funtool.analysis
import funtool.logger

GroupMeasure = collections.namedtuple('GroupMeasure',['measure_name','measure_module','measure_function','analysis_selectors','grouping_selectors','parameters'])

# A GroupMeasure is used with an AnalysisCollection and a StateCollection to measure a Group in the StateCollection
#   Unlike State measures, a grouping selector is required
#   Each member of the grouping will have a new key added to it's measures (or updated if the key already exists)
#
# measure_name          a string identifying the measure ( from the key in the YAML measure definition )
# measure_module        a string indicating where the measure_function is defined
# measure_function      a string with the name of the function which measures the group
# analysis_selectors       a list of selectors which are run sequentially to update the AnalysisCollection
# grouping_selectors    a list of group_selectors which are used to create groups in the StateCollection before any analysis is run
# parameters            a dict of parameters passed to the measure 
#
#   After measuring each member of the grouping, the measure process returns a StateCollection

def import_config(config_file_location, loaded_processes= None):
    new_group_measures={}
    with open(config_file_location) as f:
        yaml_config= yaml.load(f)
    for group_measure_name,group_measure_parameters in yaml_config.items():
        new_group_measure= GroupMeasure(measure_name= group_measure_name, **group_measure_parameters)
        new_group_measures[group_measure_name]= ( new_group_measure, group_measure_process(new_group_measure, loaded_processes)) 
            # for ** explination https://docs.python.org/2/tutorial/controlflow.html#tut-unpacking-arguments

    return new_group_measures


def group_measure_process(group_measure, loaded_processes): #returns a function, that accepts a state_collection, to be used as a process
    return _wrap_measure(individual_group_measure_process(group_measure), group_measure, loaded_processes)

def individual_group_measure_process(group_measure): #returns a function that accepts an analysis_collection and a state_collection
    group_measure_module = importlib.import_module(group_measure.measure_module)
    return functools.partial( getattr(group_measure_module,group_measure.measure_function), group_measure )

def _wrap_measure(individual_group_measure_process, group_measure, loaded_processes): 
    """
    Creates a function on a state_collection, which creates analysis_collections for each group in the collection.
    """
    def wrapped_measure(state_collection,overriding_parameters=None,loggers=None):
        if loggers == None:
            loggers = funtool.logger.set_default_loggers()
        if loaded_processes != None :
            if group_measure.grouping_selectors != None:
                for grouping_selector_name in group_measure.grouping_selectors:
                    state_collection= funtool.state_collection.add_grouping(state_collection, grouping_selector_name, loaded_processes) 
                    for group in state_collection.groups_dict[grouping_selector_name]:
                        analysis_collection = funtool.analysis.AnalysisCollection(None,group,[])
                        if group_measure.analysis_selectors != None:
                            for analysis_selector in group_measure.analysis_selectors:
                                analysis_collection = loaded_processes["analysis_selector"][analysis_selector].process_function(analysis_collection,state_collection)
                        if analysis_collection != None:
                            individual_group_measure_process(analysis_collection,state_collection)
        return state_collection
    return wrapped_measure
        


def get_measure_parameters(group_measure, overriding_parameters):
    measure_parameters= group_measure.parameters
    if overriding_parameters != None:
        if measure_parameters is None:
            measure_parameters = {}
        for param, val in overriding_parameters.items():
            measure_parameters[param] = val
    return measure_parameters

