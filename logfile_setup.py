"""Create consistent logger for all parts of alma_rest"""

import logging
from os import environ

log_format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format_string)

logfile_dir_path = environ['ALMA_REST_LOGFILE_DIR']
logfile_path = logfile_dir_path + 'alma_rest.log'
logging.basicConfig(
    format=log_format_string,
    filename=logfile_path,
    level=logging.INFO
)


def log_to_stdout(created_logger: logging.logger):
    log_console = logging.StreamHandler()
    log_console.setFormatter(log_formatter)
    created_logger.addHandler(log_console)
