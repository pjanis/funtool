# Defines a group along with helpful functions to create groups 

import collections

Group = collections.namedtuple('Group',['group_selector_name','states','measures','meta','data'] )

# A group is a collection of states and measures on that collection.
# 
# group_selector_name       a string containing the name of the group selector used to create the group
# states                    a list of states in the group
# measures                  a dict of measures on the group with the measure name as a key and the result as the value
# meta                      a dict of useful information about the group. 
# data                      a dict of data for the group. 
#   For example, if the group is defined externally, maybe in a database, what database information identifies it


# function to create a group and add entries to all the state's group_dict 
def create_group(group_selector_name,states,measures,meta,data):         
    new_group = Group(group_selector_name,states,measures,meta,data)
    for state in states:
        add_group_reference_to_state(new_group, state)
    return new_group

def add_state_to_group(group,state):
    group.states.append(state)
    add_group_reference_to_state(group,state)
    return group

def add_group_reference_to_state(group, state):
    if state.groupings.get(group.group_selector_name, None) is None:
        state.groupings[group.group_selector_name] = [ group ]
    else:
        state.groupings[group.group_selector_name]+= [ group ]
    return state
