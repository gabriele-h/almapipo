"""Create consistent logger for all parts of alma_rest"""

import logging
from os import environ

log_format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format_string)


def create_logger(name):
   created_logger = logging.getLogger(name)
   return created_logger


def log_to_file(created_logger):
   logfile_dir_path = environ['ALMA_REST_LOGFILE_DIR']
   logfile_path = logfile_dir_path + 'alma_rest.log'
   logfile_handler = logging.FileHandler(logfile_path)
   logfile_handler.setFormatter(log_formatter)
   created_logger.addHandler(logfile_handler)


def log_to_stdout(created_logger):
   log_console = logging.StreamHandler()
   log_console.setFormatter(log_formatter)
   created_logger.addHandler(log_console)
