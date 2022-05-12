"""Create consistent logger for all parts of almapipo"""

import logging
from os import environ
from pathlib import Path

log_format_string = "%(asctime)s - %(name)s - %(threadName)s - " \
                    "%(levelname)s - %(message)s"
log_formatter = logging.Formatter(log_format_string)

logfile_dir_path = Path(environ["ALMA_REST_LOGFILE_DIR"])
logfile_path = logfile_dir_path / "almapipo.log"

logging.basicConfig(
    format=log_format_string,
    filename=logfile_path,
    level=logging.INFO
)


def log_to_stdout(logger_name: logging.getLogger) -> None:
    """
    For scripts called from commandline, provide ability to log directly to
    standard out.
    :param logger_name: Logger of the invoking script.
    :return: None
    """
    log_console = logging.StreamHandler()
    log_console.setFormatter(log_formatter)
    logger_name.addHandler(log_console)
