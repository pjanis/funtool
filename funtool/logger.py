# Contains the setup of all the system loggers

import logging
import collections
import os
import sys

Loggers = collections.namedtuple('Loggers',['analysis_logger','process_logger','status_logger'])

def load_loggers(log_base_dir, analysis_time, analysis_name, analysis_uuid, log_level=logging.WARN):
    logger_dir= os.path.join(log_base_dir,'history',analysis_time, analysis_name)
    logger_id= ('_').join([analysis_time,str(analysis_uuid)]).replace('.','_')
    if not os.path.exists(logger_dir): os.makedirs(logger_dir)
    analysis_logger= load_analysis_logger(logger_dir, logger_id, log_level) 
    process_logger= load_process_logger(logger_dir, logger_id, log_level) 
    status_logger= load_status_logger(logger_dir, logger_id, log_level) 
    return Loggers( analysis_logger, process_logger, status_logger )


def load_analysis_logger(log_dir, logger_id, log_level):
    logger= logging.getLogger(logger_id)
    analysis_log= logging.FileHandler(os.path.join(log_dir,'analysis.log'))
    analysis_log.setLevel(log_level)
    analysis_log_format= logging.Formatter('%(message)s')
    analysis_log.setFormatter(analysis_log_format)
    logger.addHandler(analysis_log)
    console_log= logging.StreamHandler(sys.stdout)
    console_log.setLevel(log_level)
    console_log.setFormatter(analysis_log_format)
    logger.addHandler(console_log)
    return logger

def load_process_logger(log_dir, logger_id, log_level):
    logger= logging.getLogger(str(logger_id)+'_process')
    process_log= logging.FileHandler(os.path.join(log_dir,'process.log'))
    process_log.setLevel(log_level)
    process_log_format= logging.Formatter('%(message)s')
    process_log.setFormatter(process_log_format)
    logger.addHandler(process_log)
    return logger


def load_status_logger(log_dir, logger_id, log_level):
    logger= logging.getLogger(str(logger_id)+'_status')
    status_log= logging.FileHandler(os.path.join(log_dir,'status.log'))
    status_log.setLevel(log_level)
    status_log_format= logging.Formatter('%message)s')
    status_log.setFormatter(status_log_format)
    logger.addHandler(status_log)
    return logger

def set_default_loggers(): #Creates a default logger set based on the most recent timestamp
    known_logger_ids= list(set([ key[0:67] for key in logging.Logger.manager.loggerDict.keys()]))
    last_logger_id= sorted(known_logger_ids)[-1]
    return Loggers( logging.getLogger(last_logger_id), logging.getLogger(last_logger_id+'_process'),logging.getLogger(last_logger_id+'_status'))


