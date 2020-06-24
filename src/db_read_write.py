""" Read and write to DB

The DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, done, error)
* Store which start time of the job triggered the DB-entry
"""

from datetime import datetime
from logging import getLogger

try:
    from typing import OrderedDict
except ImportError:
    from typing import MutableMapping
    OrderedDict = MutableMapping

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import db_setup
import logfile_setup

# Logfile
logger = getLogger(__name__)


def main():
    """
    When used from commandline, the module will test the database
    connection and give according information on stdout. Please set
    env var ALMA_REST_DB_VERBOSE to 1 for the necessary feedback.
    :return: None
    """
    logfile_setup.log_to_stdout(logger)

    db_engine = create_db_engine(True)
    db_engine.connect()


def get_record_from_fetched_records(alma_ids: str):
    """
    For a comma separated string of Alma IDs query for the record's most
    most recently saved XML in the table fetched_records.
    :param alma_ids: Comma separated string of Alma IDs to identify the record.
    :return: SQLAlchemy query object of the record.
    """
    db_session = create_db_session()
    record_query = db_session.query(
        db_setup.FetchedRecords
    ).filter_by(
        alma_id=alma_ids
    ).order_by(
        'job_timestamp'
    ).limit(1)
    return record_query.first()


def update_job_status_for_alma_id(status: str,
                                  alma_id: str,
                                  job_timestamp: datetime,
                                  session: Session,
                                  action: str = 'GET'):
    """
    For a given alma_id and job_timestamp update the job_status in table job_status_per_id.
    :param status: New status to be set.
    :param alma_id: Alma ID to set the status for.
    :param job_timestamp: Job for which the status should be changed.
    :param session: Session to be used for the manipulation.
    :param action: As in job_status_per_id, possible values are "DELETE", "GET", "POST" and "PUT".
    :return: None
    """
    list_of_matched_rows = session.query(
        db_setup.JobStatusPerId
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        alma_id=alma_id
    ).filter_by(
        job_action=action
    )
    list_of_matched_rows[0].job_status = status


def get_list_of_ids_by_status_and_action(status: str, action: str, job_timestamp: datetime, session: Session):
    """
    From table job_status_per_id get all Alma IDs that match the status
    given as the parameter.
    :param status: As in job_status_per_id, possible values are "new", "done" and "error".
    :param action: As in job_status_per_id, possible values are "DELETE", "GET", "POST" and "PUT".
    :param session: DB session to connect to.
    :param job_timestamp: Timestamp to identify the job responsible for the ID.
    :return: List of IDs.
    """
    list_of_ids = session.query(
        db_setup.JobStatusPerId.alma_id
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        job_status=status
    ).filter_by(
        job_action=action
    )
    return list_of_ids


def add_sent_record_to_session(alma_id: str, record_data, job_timestamp: datetime, session: Session):
    """
    Create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line per Alma record with the data to be sent via Alma API.
    :param alma_id: Alma ID for one specific record.
    :param record_data: Record to be sent via Alma API.
    :param job_timestamp: Identifier of the job causing the DB-entry.
    :param session: DB session to add the lines to.
    :return: None
    """
    line_for_table_sent_records = db_setup.SentRecords(
        alma_id=alma_id,
        alma_record=record_data,
        job_timestamp=job_timestamp,
    )
    session.add(line_for_table_sent_records)


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


def add_csv_line_to_session(csv_line: OrderedDict, job_timestamp, session: Session, action: str = 'GET'):
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line to source_csv and one to job_status_per_id.
    :param csv_line: Ordered dictionary of values from a line of the input file.
    :param job_timestamp: Timestamp to identify the job which created the line.
    :param session: DB session to add the data to.
    :param action: As in job_status_per_id, possible values are "DELETE", "GET", "POST" and "PUT".
    :return: None
    """
    line_for_table_source_csv = db_setup.SourceCsv(
        job_timestamp=job_timestamp,
        csv_line=csv_line
    )
    session.add(line_for_table_source_csv)
    add_alma_ids_to_job_status_per_id(list(csv_line.values())[0], action, job_timestamp, session)


def add_alma_ids_to_job_status_per_id(alma_id: str, action: str, job_timestamp, session: Session):
    """
    For a string of Alma IDs create an entry in job_status_per_id.
    :param alma_id: IDs of the record to be manipulated.
    :param action: REST action - GET, PUT, POST or DELETE
    :param job_timestamp: Timestamp to identify the job which created the line.
    :param session: DB session to add the data to.
    :return:
    """
    line_for_table_job_status_per_id = db_setup.JobStatusPerId(
        job_timestamp=job_timestamp,
        alma_id=alma_id,
        job_status='new',
        job_action=action
    )
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


def create_db_engine(verbosity: bool = db_setup.does_sqlalchemy_log):
    """
    Create the DB engine according to the information provided in env vars.
    :return: DB engine.
    """
    connection_params = db_setup.prepare_connection_params_from_env()
    db_engine = create_engine(connection_params, echo=verbosity)
    return db_engine


if __name__ == "__main__":
    main()
