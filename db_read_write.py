""" Read and write to DB

The DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, done, error)
* Store which start time of the job triggered the DB-entry
"""

import logging
from datetime import datetime
from typing import OrderedDict

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import db_setup
import input_read
import logfile_setup

# Timestamp for the Script-Run as inserted in the database
job_timestamp = datetime.now()

# Logfile
logger = logging.getLogger(__name__)
logger.info(f"Starting with Job-ID {job_timestamp}")


def main():
    """
    When used from commandline, the module will test the database
    connection and give according information on stdout.
    :return: None
    """
    logfile_setup.log_to_stdout(logger)

    db_engine = create_db_engine()
    db_engine.connect()


def import_csv_to_db_tables(file_path: str, action: str = '', validation: bool = True):
    """
    Imports a whole csv or tsv file to the table source_csv.
    Imports valid Alma-IDs to table job_status_per_id.
    Checks for file existence first.
    NOTE: If no action (GET, PUT, POST or DELETE) is provided,
    it will default to an empty string.
    :param file_path: Path to the CSV file to be imported.
    :param action: REST action - GET, PUT, POST or DELETE, defaults to empty string.
    :param validation: If set to "False", the first column will not be checked for validity. Defaults to True.
    :return: None
    """
    if input_read.check_file_path(file_path):
        session = create_db_session()
        csv_generator = input_read.read_csv_contents(file_path, validation)
        for csv_line in csv_generator:
            # noinspection PyTypeChecker
            add_csv_line_to_session(csv_line, session, action)
        session.commit()
    else:
        logger.error('No valid file path provided.')


def add_csv_line_to_session(csv_line: OrderedDict, session: Session, action: str = ''):
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line to source_csv and one to job_status_per_id.
    :param csv_line: Ordered dictionary of values from a line of the input file.
    :param session: DB session to add the data to.
    :param action: REST action - GET, PUT, POST or DELETE
    :return: None
    """
    line_for_table_source_csv = db_setup.SourceCsv(
        job_timestamp=job_timestamp,
        csv_line=csv_line
    )
    line_for_table_job_status_per_id = db_setup.JobStatusPerId(
        job_timestamp=job_timestamp,
        alma_id=list(csv_line.values())[0],
        job_status='new',
        job_action=action
    )
    session.add(line_for_table_source_csv)
    session.add(line_for_table_job_status_per_id)


def create_db_session():
    """
    Create a DB session to manipulate the contents of the DB.
    :return: Session for connection to the DB.
    """
    db_engine = create_db_engine()
    DBSession = sessionmaker(bind=db_engine)
    session = DBSession()
    return session


def create_db_engine():
    """
    Create the DB engine according to the information provided in env vars.
    :return: DB engine.
    """
    connection_params = db_setup.prepare_connection_params_from_env()
    db_engine = create_engine(connection_params, echo=True)
    return db_engine


if __name__ == "__main__":
    main()
