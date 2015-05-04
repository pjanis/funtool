# Defines a State Collection, which is a collection of states along with their associated groups

import collections
import funtool.analysis

StateCollection = collections.namedtuple('StateCollection',['states','groupings'])

# A StateCollection is the default collection for a funtool. It consists of a list of states (from state.py)
# along with groupings, a dict, which has selector names as keys ( see selector.py ) and a list of groups (from group.py)  

def join_state_collections( collection_a, collection_b):
    """
    Warning: This is a very naive join. Only use it when measures and groups will remain entirely within each subcollection.

    For example: if each collection has states grouped by date and both include the same date, then the new collection 
        would have both of those groups, likely causing problems for group measures and potentially breaking many things.

    """
    
    return StateCollection(
            (collection_a.states + collection_b.states), 
            { group_selector_method:(collection_a.groupings.get(group_selector_method,[]) + collection_b.groupings.get(group_selector_method,[]))
                for group_selector_method in set( list(collection_a.groupings.keys()) + list(collection_b.groupings.keys()) ) })


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

