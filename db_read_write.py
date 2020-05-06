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


def import_csv_file_to_source_csv_table(file_path: str):
    """
    Imports a whole csv or tsv file to the table source_csv.
    Checks for file existence first.
    :param file_path: Path to the CSV file to be imported.
    :return: None
    """
    if input_read.check_file_path(file_path):
        session = create_db_session()
        csv_generator = input_read.read_csv_contents(file_path)
        for csv_line in csv_generator:
            add_line_to_session_for_source_csv_table(csv_line, session)
        session.commit()


def add_line_to_session_for_source_csv_table(csv_line: OrderedDict, session: Session):
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    create an entry in the database that identifies the job
    responsible for the entry (job_id).
    :param csv_line: Ordered dictionary of values from a line of the input file.
    :param session: DB session to add the data to.
    :return: None
    """
    line_for_table_source_csv = db_setup.SourceCsv(job_timestamp=job_timestamp, csv_line=csv_line)
    session.add(line_for_table_source_csv)


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
