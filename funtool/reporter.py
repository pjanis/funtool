# Defines a reporter

import collections
import yaml
import importlib
import functools
import os

import funtool.lib.config_parse


Reporter = collections.namedtuple('Reporter',['reporter_module','reporter_function','parameters'])

# An reporter contains three attributes,
# reporter_module       this gives the location of the file which defines the reporter
# reporter_function     this gives the function to be used to create the state_collection
# parameters            this is a dict with the paramaters needed by the reporter


class ReporterError(Exception):
    pass

def reporter_process(reporter): #returns a function, that accepts a state_collection, to be used as a process
    reporter_module = importlib.import_module(reporter.reporter_module)
    return functools.partial( getattr(reporter_module,reporter.reporter_function), reporter )

import_config= functools.partial(funtool.lib.config_parse.import_config, Reporter, reporter_process)   





def get_default_save_path(reporter_parameters):
    if reporter_parameters.get('analysis_start_time') != None:
        save_path= os.path.join(reporter_parameters['save_directory'],
            "history",
            reporter_parameters['analysis_start_time'])
    else:
        save_path= os.path.join(reporter_parameters['save_directory'])
    if reporter_parameters.get('save_subdirectory') != None:
        save_path= os.path.join(save_path,reporter_parameters.get('save_subdirectory'))
    return save_path


def get_parameters(reporter,overriding_parameters):
    reporter_parameters= reporter.parameters
    if overriding_parameters != None:
        for param, val in overriding_parameters.items():
            reporter_parameters[param] = val
    return reporter_parameters


def link_latest_output(output_dir):
    most_recent_output=''
    for timestamp_dir in os.listdir(os.path.join(output_dir,'history')): 
        if os.path.isdir(os.path.join(output_dir,'history',timestamp_dir)):
            if timestamp_dir > most_recent_output:
                most_recent_output= timestamp_dir
    if os.path.islink(os.path.join(output_dir,'latest')): 
        os.unlink(os.path.join(output_dir,'latest'))
    os.symlink(os.path.abspath(os.path.join(output_dir,'history',most_recent_output)),os.path.join(output_dir,'latest'))
    return True 
    
