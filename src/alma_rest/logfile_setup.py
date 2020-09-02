"""Create consistent logger for all parts of alma_rest"""

import logging
from os import environ
from pathlib import Path

log_format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_formatter = logging.Formatter(log_format_string)

logfile_dir_path = Path(environ['ALMA_REST_LOGFILE_DIR'])
logfile_path = logfile_dir_path / 'alma_rest.log'
logging.basicConfig(
    format=log_format_string,
    filename=logfile_path,
    level=logging.INFO
)


def log_to_stdout(created_logger) -> None:
    """
    For scripts called from commandline, provide ability to log directly to standard out.
    :param created_logger: Logger of the invoking script.
    :return: None
    """
    log_console = logging.StreamHandler()
    log_console.setFormatter(log_formatter)
    created_logger.addHandler(log_console)
