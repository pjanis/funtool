# Defines a reporter

import collections
import yaml
import importlib
import functools
import os



Reporter = collections.namedtuple('Reporter',['reporter_module','reporter_function','parameters'])

# An reporter contains three attributes,
# reporter_module       this gives the location of the file which defines the reporter
# reporter_function     this gives the function to be used to create the state_collection
# parameters            this is a dict with the paramaters needed by the reporter


class ReporterError(Exception):
    pass

def import_config(config_file_location):
    new_reporters={}
    with open(config_file_location) as f:
        yaml_config= yaml.load(f)
    for reporter_name,reporter_parameters in yaml_config.items():
        new_reporter= Reporter(**reporter_parameters)
        new_reporters[reporter_name]= (new_reporter, reporter_process(new_reporter)) 
            # for ** explination https://docs.python.org/2/tutorial/controlflow.html#tut-unpacking-arguments

    return new_reporters


def reporter_process(reporter): #returns a function, that accepts a state_collection, to be used as a process
    reporter_module = importlib.import_module(reporter.reporter_module)
    return functools.partial( getattr(reporter_module,reporter.reporter_function), reporter )
   



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
    
