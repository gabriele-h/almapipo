""" Read and write to DB

The DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, done, error)
* Store which start time of the job triggered the DB-entry
"""

from datetime import datetime
from logging import getLogger
from typing import Iterable
from xml.etree.ElementTree import fromstring, Element

try:
    from typing import OrderedDict
except ImportError:
    from typing import MutableMapping
    OrderedDict = MutableMapping

from sqlalchemy import func, String
from sqlalchemy.orm import Session

from . import db_setup
from . import logfile_setup

# Logfile
logger = getLogger(__name__)


def check_data_sent_equals_response(
        alma_id: str,
        job_timestamp: datetime,
        session: Session) -> bool:
    """
    For given alma_id and job_timestamp check if the data sent via PUT/POST
    and the data received in the API's response are the same. If no data is
    available in one of the two tables (sent_records and put_post_responses)
    this check will also return False.
    :param alma_id: Comma separated string of Alma IDs to identify the record
    :param job_timestamp: Job that created the entry in source_csv
    :param session: Session to be used for the check.
    :return: True if matches, False if non-existent or does not match.
    """
    sent_id = func.concat(db_setup.SentRecords.alma_id, db_setup.SentRecords.job_timestamp)
    received_id = func.concat(db_setup.PutPostResponses.alma_id, db_setup.PutPostResponses.job_timestamp)

    record_sent = session.query(
        db_setup.SentRecords
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        alma_id=alma_id
    )

    record_received = session.query(
        db_setup.PutPostResponses
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        alma_id=alma_id
    )

    sent_received_matching = session.query(
        db_setup.PutPostResponses
    ).join(
        db_setup.SentRecords,
        sent_id == received_id
    ).filter(
        db_setup.SentRecords.alma_record.cast(String) == db_setup.PutPostResponses.alma_record.cast(String)
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        alma_id=alma_id
    )

    if record_sent.count() == 0 or record_received.count() == 0:
        logger.error(f'No data in either sent_records or put_post_responses for {alma_id} and {job_timestamp}.')
        return False

    if sent_received_matching.count() > 0:
        return True
    else:
        logger.warning(f'Data in sent_records and put_post_responses for {alma_id} and {job_timestamp} did not match.')
        return False


def get_value_from_source_csv(
        alma_id_name: str,
        alma_id: str,
        job_timestamp: datetime,
        json_key: str) -> str:
    """
    For a given string of alma_id and job_timestamp, retrieve a
    specific value from the csv as it was saved in json-format in source_csv table.
    :param alma_id_name: Key of the alma_id, heading of first column in csv
    :param alma_id: Comma separated string of Alma IDs to identify the record
    :param job_timestamp: Job that created the entry in source_csv
    :param json_key: Heading of the column that has the desired information
    :return: Value from source_csv json for json_key
    """
    db_session = db_setup.create_db_session()
    value_query = db_session.query(
        db_setup.SourceCsv
    ).filter(
        db_setup.SourceCsv.csv_line[alma_id_name].astext == alma_id
    ).filter_by(
        job_timestamp=job_timestamp
    )
    json_value = value_query.first().csv_line[json_key]
    db_session.close()
    return json_value


def get_records_by_timestamp(job_timestamp: datetime) -> Iterable[Element]:
    """
    For a given job_timestamp get all fetched_record.alma_record (XML) from the database.
    :param job_timestamp: Job that created the entry in fetched_records
    :return: XML of the records
    """
    db_session = db_setup.create_db_session()

    record_query = db_session.query(
        db_setup.FetchedRecords.alma_record
    ).filter_by(
        job_timestamp=job_timestamp
    )
    db_session.close()

    for result in record_query.all():
        yield result[0]


def get_most_recent_version_from_fetched_records(alma_id: str):
    """
    For a comma separated string of Alma IDs query for the record's
    most recently saved XML in the table fetched_records.
    :param alma_id: Comma separated string of Alma IDs to identify the record.
    :return: SQLAlchemy query object of the record.
    """
    db_session = db_setup.create_db_session()
    record_query = db_session.query(
        db_setup.FetchedRecords
    ).filter_by(
        alma_id=alma_id
    ).order_by(
        db_setup.FetchedRecords.job_timestamp.desc()
    ).limit(1)
    db_session.close()
    return record_query.first()


def update_job_status(status: str,
                      alma_id: str,
                      method: str,
                      job_timestamp: datetime,
                      session: Session) -> None:
    """
    For a given alma_id and job_timestamp update the job_status in table job_status_per_id.
    :param status: New status to be set.
    :param alma_id: Alma ID to set the status for.
    :param method: As in job_status_per_id, possible values are "DELETE", "GET", "POST" and "PUT".
    :param job_timestamp: Job for which the status should be changed.
    :param session: Session to be used for the manipulation.
    :return: None
    """
    list_of_matched_rows = session.query(
        db_setup.JobStatusPerId
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        alma_id=alma_id
    ).filter_by(
        job_action=method
    )
    list_of_matched_rows[0].job_status = status


def get_list_of_ids_by_status_and_method(status: str, method: str, job_timestamp: datetime, session: Session) -> list:
    """
    From table job_status_per_id get all Alma IDs that match the status
    given as the parameter.
    :param status: As in job_status_per_id, possible values are "new", "done" and "error".
    :param method: As in job_status_per_id, possible values are "DELETE", "GET", "POST" and "PUT".
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
        job_action=method
    )
    return list_of_ids


def add_put_post_response(alma_id: str, record_data: str, job_timestamp: datetime, session: Session) -> None:
    """
    Create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line per Alma record with the data retrieved via Alma API.
    :param alma_id: Alma ID for one specific record.
    :param record_data: Response retrieved via Alma API.
    :param job_timestamp: Identifier of the job causing the DB-entry.
    :param session: DB session to add the lines to.
    :return: None
    """
    record_data_xml = fromstring(record_data)
    line_for_table_put_post_responses = db_setup.PutPostResponses(
        alma_id=alma_id,
        alma_record=record_data_xml,
        job_timestamp=job_timestamp,
    )
    session.add(line_for_table_put_post_responses)


def add_sent_record(alma_id: str, record_data: bytes, job_timestamp: datetime, session: Session) -> None:
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
    record_data_xml = fromstring(record_data)
    line_for_table_sent_records = db_setup.SentRecords(
        alma_id=alma_id,
        alma_record=record_data_xml,
        job_timestamp=job_timestamp,
    )
    session.add(line_for_table_sent_records)


def add_response_content_to_fetched_records(
        alma_id: str,
        record_data,
        job_timestamp: datetime,
        session: Session) -> None:
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


def add_csv_line_to_tables(
        csv_line: OrderedDict,
        job_timestamp: datetime,
        session: Session,
        method: str) -> None:
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line to source_csv and one to job_status_per_id.
    :param csv_line: Ordered dictionary of values from a line of the input file.
    :param job_timestamp: Timestamp to identify the job which created the line.
    :param session: DB session to add the data to.
    :param method: As in job_status_per_id, possible values are "DELETE", "GET", "POST" and "PUT".
    :return: None
    """
    line_for_table_source_csv = db_setup.SourceCsv(
        job_timestamp=job_timestamp,
        csv_line=csv_line
    )
    session.add(line_for_table_source_csv)
    add_alma_id_to_job_status_per_id(list(csv_line.values())[0], method, job_timestamp, session)


def add_alma_id_to_job_status_per_id(
        alma_id: str,
        method: str,
        job_timestamp: datetime,
        session: Session) -> None:
    """
    For a string of Alma IDs create an entry in job_status_per_id.
    :param alma_id: IDs of the record to be manipulated.
    :param method: GET, PUT, POST or DELETE
    :param job_timestamp: Timestamp to identify the job which created the line.
    :param session: DB session to add the data to.
    :return: None
    """
    line_for_table_job_status_per_id = db_setup.JobStatusPerId(
        job_timestamp=job_timestamp,
        alma_id=alma_id,
        job_status='new',
        job_action=method
    )
    session.add(line_for_table_job_status_per_id)


# noinspection PyArgumentList
def log_success_rate(method: str, job_timestamp: datetime, db_session: Session) -> None:
    """
    For the current job check how many records have a specific status in job_status_per_id.
    :param method: GET, PUT, POST or DELETE
    :param job_timestamp: Timestamp to identify the job which created the line.
    :param db_session: DB session to make use of.
    :return: None
    """
    ids_done = get_list_of_ids_by_status_and_method('done', method, job_timestamp, db_session)
    ids_error = get_list_of_ids_by_status_and_method('error', method, job_timestamp, db_session)
    ids_new = get_list_of_ids_by_status_and_method('new', method, job_timestamp, db_session)
    logger.info(f"{method} was done for {ids_done.count()} record(s).")
    logger.info(f"{method} had errors for {ids_error.count()} record(s).")
    logger.info(f"{method} was not handled for {ids_new.count()} record(s).")
