# Defines an adaptor, which is used to connect to a datasource and return a StateCollection ( as defined in state_collection.py )

import collections
import yaml
import importlib
import functools


Adaptor = collections.namedtuple('Adaptor',['adaptor_module','adaptor_function','data_location'])

# An adaptor contains three attributes,
# adaptor_module      this gives the location of the file which defines the adaptor
# adaptor_function  this gives the function to be used to create the state_collection
# data_location     this is a dict with the paramaters needed by the adaptor_function to create the state_collection


class AdaptorError(Exception):
    pass

def import_config(config_file_location):
    new_adaptors={}
    with open(config_file_location) as f:
        yaml_config= yaml.load(f)
    for adaptor_name,adaptor_parameters in yaml_config.items():
        new_adaptor= Adaptor(**adaptor_parameters)
        new_adaptors[adaptor_name]= (new_adaptor, adaptor_process(new_adaptor)) 
            # for ** explination https://docs.python.org/2/tutorial/controlflow.html#tut-unpacking-arguments

    return new_adaptors


def adaptor_process(adaptor): #returns a function, that accepts a state_collection, to be used as a process
    adaptor_module = importlib.import_module(adaptor.adaptor_module)
    return functools.partial( getattr(adaptor_module,adaptor.adaptor_function), adaptor )
    

