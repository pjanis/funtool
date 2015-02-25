# Defines an analysis and provides methods to run it

# An analysis should be an ordered list of group_selectors, measures, reporters, and other analyses (i.e. analyses can be nested).

import collections 
import yaml
import functools
import uuid
import logging
import datetime
import os
import pkg_resources
import pip
import subprocess

import funtool.state_collection
import funtool.logger


Analysis = collections.namedtuple('Analysis',['name','process_identifiers','processes'])

# ProcessIdentifiers are defined in the analysis config, Processes are created internally

ProcessIdentifier = collections.namedtuple('ProcessIdentifier', ['process_type','process_name'])

# for a process, the collection is the particular namedtuple used to generate the process_fuction
Process= collections.namedtuple('Process',['collection','process_function'])


AnalysisCollection = collections.namedtuple('AnalysisCollection',['state','group','state_list'])

# An AnalysisCollection is a collection generated from a StateCollection used during part of the analysis
#
# In this collection are:
# state         a privileged state used by a process ( often the current state )
# group         a privileged group
# state_list    a privileged list of states, often from previous processes


def import_config(config_file_location):
    new_analyses=[]
    with open(config_file_location) as f:
        yaml_config= yaml.load(f)
    for individual_analysis in yaml_config:
        analysis_name, analysis_parameters = next(iter(individual_analysis.items()))
        new_analyses.append( Analysis(analysis_name, load_process_identifiers(analysis_parameters), []) )
    return new_analyses

def load_process_identifiers(analysis_parameters):
    return [ ProcessIdentifier(*_expand_process_identifiers(process_parameters)) for process_parameters in analysis_parameters ]        

def load_processes(analysis,known_processes, known_analyses):
    check_process_existence(analysis,known_processes,known_analyses)
    for process_id in analysis.process_identifiers:    
        if process_id.process_type == 'analysis':
            sub_analysis= load_processes(known_analyses[process_id.process_name], known_processes, known_analyses)
            analysis.processes.append(analysis_process(sub_analysis) )              
        else:
            analysis.processes.append(known_processes[process_id.process_type][process_id.process_name])
    return analysis 

def analysis_process(analysis): # returns a function which takes and returns a StateCollection and runs an analysis
    return functools.partial(run_analysis, analysis)

def run_analysis(analysis,state_collection=None,log_dir=None,log_level=logging.WARN):
    analysis_start_time= _analysis_time_str() 
    loggers= _load_loggers(analysis, analysis_start_time, log_dir, log_level)
    overriding_parameters={ 'analysis_start_time':analysis_start_time }
    loggers.analysis_logger.warn('Analysis Overriding Parameters: %s'% overriding_parameters)
    if state_collection == None :
        state_collection = funtool.state_collection.StateCollection([],{})        
    for idx,process in enumerate(analysis.processes):
        loggers.analysis_logger.warn("\tRunning step "+ str(idx+1) + " : " + analysis.process_identifiers[idx].process_name )
        new_state_collection= process.process_function(state_collection,overriding_parameters,loggers)
        state_collection= _test_and_update_state_collection(new_state_collection,state_collection,loggers)
    _link_latest_logs(log_dir)
    _log_analysis_complete(loggers)
    return state_collection


# TODO needs to be made recursive for measures, etc...
def check_process_existence(analysis,known_processes, known_analyses):
    missing_processes= False
    for process_id in analysis.process_identifiers:    
        try:
            if process_id.process_type == 'analysis':
                check_process_existence(known_analyses[process_id.process_name], known_processes, known_analyses)
            else:
                known_processes[process_id.process_type][process_id.process_name]
        except KeyError:
            print("Process " + process_id.process_type + " "+ process_id.process_name + " is unknown.")
            print("Known Process are:")
            for (known_process_type, known_processes_of_type) in known_processes.items():
                for (known_process_name, known_process) in known_processes_of_type.items():
                    print(known_process_type + ":" + known_process_name) 
            missing_processes= True
    if missing_processes :
        raise Exception("Missing Processes")
    return True


def _load_loggers(analysis,analysis_start_time, log_dir,log_level):
    analysis_uuid= uuid.uuid4()
    loggers= funtool.logger.load_loggers(log_dir, analysis_start_time, analysis.name, analysis_uuid,log_level)
    _log_analysis_start(loggers, analysis, analysis_start_time)
    _log_module_versions(loggers)
    _log_version_control(loggers)
    return loggers

def _log_analysis_start(loggers,analysis, analysis_start_time):
    loggers.analysis_logger.warn('Analysis Name: %s'% analysis.name )
    loggers.analysis_logger.warn('Analysis Start Time: %s'% analysis_start_time) 
    return loggers

def _log_module_versions(loggers):
    for package in pip.get_installed_distributions():
        if 'funtool' in package.project_name:
            loggers.analysis_logger.warn('%s Version: %s'% (package.project_name,pkg_resources.get_distribution(package.project_name).version))
    return loggers

def _log_version_control(loggers): #git only for now
    try:
        commit_hash= subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf8').rstrip()
        loggers.analysis_logger.warn('Analysis Git Commit: %s'% commit_hash)
        git_status = subprocess.check_output(['git','status','--porcelain']).decode('utf8')
        if len(git_status) is 0:
            loggers.analysis_logger.warn('Analysis Git Status: Clean')
        else:
            loggers.analysis_logger.warn('Analysis Git Status: Dirty')
            for status_line in git_status.split("\n"):
                loggers.analysis_logger.warn("\t"+status_line)
            
    except Exception:
        pass
    return loggers


def _log_analysis_step(loggers):
    return loggers

def _log_analysis_complete(loggers):
    loggers.analysis_logger.warn('Analysis Complete Time: %s'% _analysis_time_str())
    return loggers

def _analysis_time_str():
    return str(datetime.datetime.utcnow()).replace(' ','_').replace(':','.')+'_UTC'

def _link_latest_logs(log_dir):
    most_recent_logs=''
    for timestamp_dir in os.listdir(os.path.join(log_dir,'history')): 
        if os.path.isdir(os.path.join(log_dir,'history',timestamp_dir)):
            if timestamp_dir > most_recent_logs:
                most_recent_logs= timestamp_dir
    if os.path.islink(os.path.join(log_dir,'latest')): 
        os.unlink(os.path.join(log_dir,'latest'))
    os.symlink(os.path.abspath(os.path.join(log_dir,'history',most_recent_logs)),os.path.join(log_dir,'latest'))
    return True 

def _test_and_update_state_collection(new_state_collection,old_state_collection,loggers):
    if isinstance(new_state_collection, funtool.state_collection.StateCollection):
        return new_state_collection
    else:
        loggers.analysis_logger.error("Error in process : StateCollection not returned")
        loggers.analysis_logger.warn("Continuing with previous StateCollection")
        return old_state_collection

def _expand_process_identifiers(process_parameters_dict):
    return list(next(iter(process_parameters_dict.items())))
 
