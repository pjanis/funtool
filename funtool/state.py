# Defines of a state

import collections

State = collections.namedtuple('State',['id','data','measures','meta','groupings'] )

# A state is the basic unit of analysis. It can be anything that can be coerced into the given form,
# though most measures will assume a particular structure for data

# id            a string id for the state
# data          the primary raw data for the state, for example JSON save information
# measures      a dict of measures on the state. The key is the measure name, and the value is whatever
#       is returned by the funtool. It can be left empty to be populated in the analysis, or it can 
#       be partially populated by an adaptor when a value already exists.
# meta          a dict of any set of data about the state, such as student_id, project_id, etc.
#       Important meta keys will be listed below along with a short description of the use
# groupings   a dict which contains the selector method used to create the groups as a key
#       and a list groups that this state is a member of as the value
#       For Example: if states are grouped by project id, then the project id selector name would
#           be the key, and the value would be a single valued list of the group this state was in


# META
#=====
#
# These are useful meta pairs. They are not neccessary for all states. These are only recommended usages.
#
#-----
# database_id   a dict which contains three values that identify the state in a database
#       The three values are:
#           table_name      the table that identifies the state
#           primary_keys    a list of columns that identifies the state, normally just the primary key
#           primary_values  a list of values that correspond with the primary_keys to identify the state
#
# user_id       a string identifying which user created the state  
#            
# project_id    a string identifying the project the state is part of
#
# creation_time a datetime for the state ( limited to microsecond percision, use custom type for greater accuracy )
# 
# filename      a string with the file the state comes from
#
# directory     a string with the location of the file

