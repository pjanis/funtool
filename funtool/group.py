# Defines a group along with helpful functions to create groups 

import collections

Group = collections.namedtuple('Group',['group_selector_name','states','measures','meta'] )

# A group is a collection of states and measures on that collection.
# 
# group_selector_name       a string containing the name of the group selector used to create the group
# states                    a list of states in the group
# measures                  a dict of measures on the group with the measure name as a key and the result as the value
# meta                      a dict of useful information about the group. 
#   For example, if the group is defined externally, maybe in a database, what database information identifies it


# function to create a group and add entries to all the state's group_dict 
def create_group(group_selector_name,states,measures,meta):         
    new_group = Group(group_selector_name,states,measures,meta)
    for state in states:
        if state.groups_dict.get(group_selector_name, None) == None:
            state.groups_dict[group_selector_name] = [ new_group ]
        else:
            state.groups_dict[group_selector_name]+= [ new_group ]
    return new_group
