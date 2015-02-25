import importlib
import os
import inspect

import funtool
import funtool.analysis

# Configuration Locations
# processes defined in the last location take precedence

funtool_path= os.path.dirname(inspect.getfile(funtool))

default_locations= [
    funtool_path,
    os.path.join('.','config')
]

primary_analyses_directory= os.path.join('.','analyses')


default_log_dir= os.path.join('.','logs')

#supplemental analyses directories, intended for sub-analyses
analyses_directories= [
    'analysis',
    'analyses'
]

# For processes that don't depend on other processes
independent_process_types= [    
    'adaptor',
    'analysis_selector',
    'grouping_selector',
    'reporter'
]

# For processes that may need other processes loaded, dependent process load order may matter
dependent_process_types = [
    'state_measure',
    'group_measure'
]

# This could probably be replaced with inflect, but for one instance it's probably not worth it
def _process_type_default_directory(process_type):
    return {
        'adaptor':'adaptors',
        'analysis_selector':'analysis_selectors',
        'state_measure':'state_measures',
        'grouping_selector':'grouping_selectors',
        'group_measure':'group_measures',
        'reporter':'reporters'
    }[process_type]


# API Functions

def load_config(locations=default_locations,independent_process_types=independent_process_types, dependent_process_types=dependent_process_types):
    loaded_processes={}
    for process_type in independent_process_types:
        loaded_processes[process_type]=_load_from_locations(process_type,locations)
    for process_type in dependent_process_types:
        loaded_processes[process_type]=_load_dependent_from_locations(process_type,locations,loaded_processes)
    return loaded_processes

def load_primary_analyses(primary_analyses_location= primary_analyses_directory):
    primary_analyses=[]
    for config_file in _available_config_files(primary_analyses_directory):
        primary_analyses.append( funtool.analysis.import_config(config_file) )   
    return [ analysis for config_analyses in primary_analyses for analysis in config_analyses ]
     

def load_known_analyses(locations=default_locations, primary_analyses=None):
    if primary_analyses == None:
        primary_analyses = load_primary_analyses()
    known_analyses = {}
    for location in locations:
        for analyses_directory in analyses_directories:
            for possible_analyses_directory in _mangle(analyses_directory):
                dir_path = os.path.join(location, possible_analyses_directory )
                for config_file in _available_config_files(dir_path):
                    config_file_analyses= funtool.analysis.import_config(config_file)
                    for config_file_analysis in config_file_analyses:
                       known_analyses[config_file_analysis.name] = config_file_analysis    
    for primary_analysis in primary_analyses:
       known_analyses[primary_analysis.name] = primary_analysis    
    return known_analyses     

def prepare_analyses(loaded_processes=None,known_analyses=None, primary_analyses=None):
    if primary_analyses == None:
        primary_analyses = load_primary_analyses()
    if known_analyses == None:
        known_analyses = load_known_analyses(primary_analyses= primary_analyses)
    if loaded_processes == None:
        loaded_processes = load_config()
    return [ funtool.analysis.load_processes(analysis,loaded_processes,known_analyses) for analysis in primary_analyses ]
   

def run_analyses(prepared_analyses=None,log_dir=default_log_dir):
    """
        If all defaults are ok, this should be the only function needed to run the analyses.
    """
    if prepared_analyses == None:
        prepared_analyses = prepare_analyses()
    state_collection = funtool.state_collection.StateCollection([],{})
    for analysis in prepared_analyses:
        state_collection= funtool.analysis.run_analysis(analysis, state_collection, log_dir)
    return state_collection
    
       

# Internal Functions

def _load_from_locations(process_type,locations):
    process_module = importlib.import_module("funtool."+process_type)
    process_config_import = getattr(process_module,"import_config")
    process_type_alts = _mangle(process_type)
    loaded_processes = {}
    for location in locations:
        for process_type_alt in process_type_alts:
            process_directory= os.path.join(location,_process_type_default_directory(process_type_alt))
            for config_file in _available_config_files(process_directory): 
                print("Loading Processes From: " + os.path.join(process_directory,config_file)) #TODO:Add to logger during preflight step
                for process_name,process in process_config_import(config_file).items():
                    loaded_processes[process_name]= funtool.analysis.Process(*process)
    return loaded_processes

def _load_dependent_from_locations(process_type,locations, preloaded_processes):
    process_module = importlib.import_module("funtool."+process_type)
    process_config_import = getattr(process_module,"import_config")
    process_type_alts = _mangle(process_type)
    loaded_processes = {}
    for location in locations:
        for process_type_alt in process_type_alts:
            process_directory= os.path.join(location,_process_type_default_directory(process_type_alt))
            for config_file in _available_config_files(process_directory): 
                for process_name,process in process_config_import(config_file, preloaded_processes).items():
                    loaded_processes[process_name]= funtool.analysis.Process(*process)
    return loaded_processes

def _available_config_files(directory):
    available_files=[]
    for root, subdirectories, files in os.walk(directory):
        for f in files:
            if f.endswith(".yaml") or f.endswith(".yml"):
                available_files.append(os.path.join(root,f))
    return sorted(available_files)

# TODO mangles a particular directory_string to give other possible strings
def _mangle(directory_string):
    return [directory_string] 
        
