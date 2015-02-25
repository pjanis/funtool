# Defines an adaptor, which is used to connect to a datasource and return a StateCollection ( as defined in state_collection.py )

import collections
import yaml
import importlib
import functools

import funtool.lib.config_parse


Adaptor = collections.namedtuple('Adaptor',['adaptor_module','adaptor_function','data_location'])

# An adaptor contains three attributes,
# adaptor_module      this gives the location of the file which defines the adaptor
# adaptor_function  this gives the function to be used to create the state_collection
# data_location     this is a dict with the paramaters needed by the adaptor_function to create the state_collection


class AdaptorError(Exception):
    pass

def adaptor_process(adaptor): #returns a function, that accepts a state_collection, to be used as a process
    adaptor_module = importlib.import_module(adaptor.adaptor_module)
    return functools.partial( getattr(adaptor_module,adaptor.adaptor_function), adaptor )
    
import_config= functools.partial(funtool.lib.config_parse.import_config, Adaptor, adaptor_process)
