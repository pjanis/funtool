# Defines a State Collection, which is a collection of states along with their associated groups

import collections
import funtool.analysis

StateCollection = collections.namedtuple('StateCollection',['states','groupings'])

# A StateCollection is the default collection for a funtool. It consists of a list of states (from state.py)
# along with groupings, a dict, which has selector names as keys ( see selector.py ) and a dict of group_keys:group (from group.py)  

def join_state_collections( collection_a, collection_b):
    """
    Warning: This is a very naive join. Only use it when measures and groups will remain entirely within each subcollection.

    For example: if each collection has states grouped by date and both include the same date, then the new collection 
        would have both of those groups, likely causing problems for group measures and potentially breaking many things.

    """
    
    return StateCollection(
            (collection_a.states + collection_b.states), 
            { grouping_name:_combined_grouping_values(grouping_name, collection_a,collection_b)
                for grouping_name in set( list(collection_a.groupings.keys()) + list(collection_b.groupings.keys()) ) })


def add_grouping(state_collection, grouping_name, loaded_processes, overriding_parameters=None):
    """
    Adds a grouping to a state collection by using the process selected by the grouping name
    
    Does not override existing groupings
    """
    if (
        grouping_name not in state_collection.groupings and
        loaded_processes != None and
        loaded_processes["grouping_selector"].get(grouping_name) != None
    ):
        state_collection = loaded_processes["grouping_selector"][grouping_name].process_function(state_collection,overriding_parameters)
    return state_collection

def add_group_to_grouping(state_collection, grouping_name, group, group_key=None):
    """
    Adds a group to the named grouping, with a given group key

    If no group key is given, the lowest available integer becomes the group key

    If no grouping exists by the given name a new one will be created

    Replaces any group with the same grouping_name and the same group_key
    """
    if state_collection.groupings.get(grouping_name) is None:
        state_collection.groupings[grouping_name]= {}
    if group_key is None:
        group_key= _next_lowest_integer(state_collection.groupings[grouping_name].keys())
    state_collection.groupings[grouping_name][group_key]= group
    return state_collection
    

def groups_in_grouping(state_collection,grouping_name):
    """
    Returns an iterable which goes over all the groups in a grouping
    
    Use instead of direct access to future proof in case of changes in StateCollection
    """
    return state_collection.groupings.get(grouping_name, {}).values()


def _combined_grouping_values(grouping_name,collection_a,collection_b):
    """
    returns a dict with values from both collections for a given grouping name

    Warning: collection2 overrides collection1 if there is a group_key conflict
    """
    new_grouping= collection_a.groupings.get(grouping_name,{}).copy()
    new_grouping.update(collection_b.groupings.get(grouping_name,{}))
    return new_grouping
   
def _next_lowest_integer(group_keys):
    """
    returns the lowest available integer in a set of dict keys
    """
    try: #TODO Replace with max default value when dropping compatibility with Python < 3.4
        largest_int= max([ int(val) for val in group_keys if _is_int(val)])
    except:
        largest_int= 0
    return largest_int + 1
    

def _is_int(val):
    """
    returns true if val can be cast as an int and false if not
    """
    try:
        int(val)
        return True
    except ValueError:
        return False

        



