""" Read and write to DB

The DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, done, error)
* Store which start time of the job triggered the DB-entry
"""

from datetime import datetime
from logging import getLogger
from typing import OrderedDict

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import db_setup
import logfile_setup

# Logfile
logger = getLogger(__name__)


def main():
    """
    When used from commandline, the module will test the database
    connection and give according information on stdout.
    :return: None
    """
    logfile_setup.log_to_stdout(logger)

    db_engine = create_db_engine()
    db_engine.connect()


def add_fetched_record_to_session(alma_id: str, record_data, job_timestamp: datetime, session: Session):
    """
    Create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line per Alma record with the data retrieved via Alma API.
    :param alma_id: Alma ID for one specific record.
    :param record_data: Record as retrieved via Alma API.
    :param job_timestamp: Identifier of the job causing the DB-entry.
    :param session: DB session to add the lines to.
    :return: None
    """
    line_for_table_fetched_records = db_setup.FetchedRecords(
        alma_id=alma_id,
        alma_record=record_data,
        job_timestamp=job_timestamp,
    )
    session.add(line_for_table_fetched_records)


def add_csv_line_to_session(csv_line: OrderedDict, job_timestamp, session: Session, action: str = ''):
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line to source_csv and one to job_status_per_id.
    :param csv_line: Ordered dictionary of values from a line of the input file.
    :param job_timestamp: Timestamp to identify the job which created the line.
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
