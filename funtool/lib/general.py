import copy
import functools



def get_parameters(process_tuple, overriding_parameters):
    tuple_parameters= copy.deepcopy(process_tuple.parameters)
    if overriding_parameters != None:
        if tuple_parameters is None:
            tuple_parameters = {}
        for param, val in overriding_parameters.items():
            tuple_parameters[param] = val
    return tuple_parameters

def get_tuple(my_dict):
    """
    Returns a tuple of the "first" item in a dict

    Useful for converting dicts with only one item 
    """ 
    try:
        return next( iter( my_dict.items() ) )
    except StopIteration:
        return ( None, None )


def sort_states(states, sort_list):
    """
    Returns a list of sorted states, original states list remains unsorted

    The sort list is a list of state field: field key pairs
        For example (as YAML):
            - data: position
            - meta: created_at
    The field_key part can be a list to simplify input
        - meta: created_at
        - meta: updated_at
    or
        - meta:
            - created_at
            - updated_at

    
    It is also possible to sort by grouping values
        For example, with a grouping called student_id:
        - groupings:
            - student_id:
                index: !!null     (optional: when null or missing it uses the first group in the grouping
                values:
                    - meta: student_id

    A key which begins with a - inverts the sort, so
        - -data: position
    is the inverse of
        - data: position

    With groupings only values can have a - to invert the sort (always on the key)
        - groupings:
            - student_id:
                index: !!null
                values:
                    - -meta: student_id
    NOT
        - -groupings: ...
        

    """
    sorted_states= states.copy()
    for sort_pair in reversed( _convert_list_of_dict_to_tuple(sort_list) ):
        if sort_pair[0].lstrip('-') in ['data','measure','meta']:
            sorted_states= _state_value_sort(sorted_states, sort_pair, _state_key_function)
        elif sort_pair[0] == 'groupings':
            for grouping in reversed(sort_pair[1]):
                sorted_states= _groupings_values_sort(sorted_states, grouping)
    return sorted_states

def _state_value_sort(states, sort_pair, key_function):
    sorted_states= states.copy()
    attribute_name= sort_pair[0].lstrip('-')
    if sort_pair[0][0] == '-':
        reverse= True
    else:
        reverse= False
    if type(sort_pair[1]) == list:
        for sort_value in reversed(sort_pair[1]):
            sorted_states= sorted(sorted_states, key= lambda state: key_function(state, attribute_name, sort_value), reverse= reverse)
    else:
        sorted_states= sorted(sorted_states, key= lambda state: key_function(state, attribute_name, sort_pair[1]), reverse= reverse)
    return sorted_states

def _groupings_values_sort(states, grouping):
    grouping_name= next(iter( grouping.keys() ))
    grouping_details= next(iter( grouping.values() ))
    grouping_index= grouping_details.get('index') or 0
    sorted_states= states.copy()
    for sort_pair in reversed(_convert_list_of_dict_to_tuple(grouping_details['values'])):
        sorted_states= _state_value_sort( sorted_states, 
            sort_pair, 
            functools.partial(_grouping_key_function, grouping_name= grouping_name, grouping_index= grouping_index))
    return sorted_states

def _state_key_function(state, attribute_name, sort_value):
    return _state_value(state, attribute_name,sort_value)

 # Since a group also has data,meta, and measures it can be treated like a state for the sort value lookup
def _grouping_key_function(state, attribute_name, sort_value, grouping_name, grouping_index):
    if len(state.groupings.get(grouping_name,[])) > grouping_index:
        return _state_value(state.groupings.get(grouping_name,[])[grouping_index], attribute_name,sort_value)
    else:
        return MinType() #Incase of a missing group

def _state_value(state, attribute_name, attribute_value): # handles None values for sort
    val= getattr(state, attribute_name,{}).get(attribute_value)
    if val is None:
        return MinType()
    else:
        return val

# TODO replace this with a function that converts all single item dicts to tuples anywhere in a list(or sublist)
def _convert_list_of_dict_to_tuple(dict_list): #converts a list of single key dicts to a list of tuples
   return [ next(iter(d.items())) for d in dict_list ]

# A min type to handle comparisons with None

@functools.total_ordering
class MinType(object):
    def __le__(self,other):
        return True
    def __eq__(self,other):
        return (self is other)
