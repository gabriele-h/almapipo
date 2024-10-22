""" Read from DB

Query the following information:
* CSV/TSV input used for lists of records
* Status of API calls for records
* API responses to PUT/POST calls
* Data sent to the API via PUT/POST calls
"""

from datetime import datetime
from logging import getLogger
from typing import Iterable
from xml.etree.ElementTree import Element

from sqlalchemy import func, String
from sqlalchemy.orm import Session, Query

from . import setup_db

# Logfile
logger = getLogger(__name__)


def check_data_sent_equals_response(
        almaid: str,
        job_timestamp: datetime,
        db_session: Session) -> bool:
    """
    For given almaid and job_timestamp check if the data sent via PUT/POST
    and the data received in the API's response are the same. Check depends on
    the two relevant database tables (sent_records and put_post_responses).
    :param almaid: Comma separated string of Alma IDs to identify the record
    :param job_timestamp: Job that created the entry in the database tables
    :param db_session: Session to be used for the check
    :return: True if matches, False if non-existent or does not match.
    """

    sent_id = func.concat(
        setup_db.SentRecords.almaid,
        setup_db.SentRecords.job_timestamp
    )
    response_id = func.concat(
        setup_db.PutPostResponses.almaid,
        setup_db.PutPostResponses.job_timestamp
    )

    if check_data_sent_and_response_exist(almaid, job_timestamp, db_session):

        sent_received_matching = db_session.query(
            setup_db.PutPostResponses
        ).join(
            setup_db.SentRecords,
            sent_id == response_id
        ).filter(
            setup_db.SentRecords.alma_record.cast(String) ==
            setup_db.PutPostResponses.alma_record.cast(String)
        ).filter_by(
            job_timestamp=job_timestamp
        ).filter_by(
            almaid=almaid
        )

        if sent_received_matching.count() > 0:
            return True

    logger.warning(f"Data in sent_records and put_post_responses for {almaid}"
                   f" and {job_timestamp} did not match.")
    return False


def check_data_sent_and_response_exist(
        almaid: str,
        job_timestamp: datetime,
        db_session: Session) -> bool:
    """
    For given almaid and job_timestamp check if the following exist:
    * data sent via PUT/POST
    * data received in the API's response
    :param almaid: Comma separated string of Alma IDs to identify the record
    :param job_timestamp: Job that created the entry in the database tables
    :param db_session: Session to be used for the check
    :return: True if both exist, False if one or both do not exist
    """

    record_sent = db_session.query(
        setup_db.SentRecords
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        almaid=almaid
    )

    record_received = db_session.query(
        setup_db.PutPostResponses
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        almaid=almaid
    )

    if record_sent.count() > 0 and record_received.count() > 0:
        return True

    logger.error(f"No data in sent_records or put_post_responses for {almaid}"
                 f" and {job_timestamp}.")
    return False


def get_value_from_source_csv(
        almaid_name: str,
        almaid: str,
        job_timestamp: datetime,
        json_key: str,
        db_session: Session) -> str:
    """
    For a given string of almaid and job_timestamp, retrieve a specific value
    from the csv as it was saved in source_csv table.
    :param almaid_name: Key of the almaid, heading of first column in csv
    :param almaid: Comma separated string of Alma IDs to identify the record
    :param job_timestamp: Job that created the entry in source_csv
    :param json_key: Heading of the column that has the desired information
    :param db_session: SQLAlchemy Session
    :return: Value from source_csv json for json_key
    """

    value_query = db_session.query(
        setup_db.SourceCsv
    ).filter(
        setup_db.SourceCsv.csv_line[almaid_name].astext == almaid
    ).filter_by(
        job_timestamp=job_timestamp
    )

    json_value = value_query.first().csv_line[json_key]

    return json_value


def get_fetched_xml_by_timestamp(
        job_timestamp: datetime,
        db_session: Session
) -> Iterable[Element]:
    """
    For a given job_timestamp get all fetched_record.alma_record (XML) from
    the database.
    :param job_timestamp: Job that created the entry in fetched_records
    :param db_session: SQLAlchemy Session
    :return: XML of the records
    """

    record_query = db_session.query(
        setup_db.FetchedRecords.alma_record
    ).filter_by(
        job_timestamp=job_timestamp
    )

    for result in record_query.all():
        yield result[0]


def get_most_recent_fetched_xml(almaid: str, db_session: Session):
    """
    For a comma separated string of Alma IDs query for the record's
    most recently saved XML in the table fetched_records.
    :param almaid: Comma separated string of Alma IDs to identify the record.
    :param db_session: SQLAlchemy Session
    :return: SQLAlchemy query object of the record.
    """

    record_query = db_session.query(
        setup_db.FetchedRecords
    ).filter_by(
        almaid=almaid
    ).order_by(
        setup_db.FetchedRecords.job_timestamp.desc()
    ).limit(1)

    return record_query.first().alma_record


def get_list_of_ids_by_status_and_method(
        status: str,
        method: str,
        job_timestamp: datetime,
        db_session: Session) -> Query:
    """
    From table job_status_per_id get all Alma IDs that match the status
    given as the parameter.
    :param status: "new", "done" or "error"
    :param method: "DELETE", "GET", "POST" or "PUT"
    :param db_session: DB session to connect to
    :param job_timestamp: Timestamp to identify the job that made the entry
    :return: List of IDs.
    """

    list_of_ids = db_session.query(
        setup_db.JobStatusPerId.almaid
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        job_status=status
    ).filter_by(
        job_action=method
    )

    return list_of_ids


def log_success_rate(
        method: str,
        job_timestamp: datetime,
        db_session: Session) -> None:
    """
    For the current job check how many records have a specific status in
    job_status_per_id.
    :param method: GET, PUT, POST or DELETE
    :param job_timestamp: Timestamp to identify the job which created the line
    :param db_session: DB session to make use of
    :return: None
    """

    ids_done = get_list_of_ids_by_status_and_method(
        "done", method, job_timestamp, db_session
    )
    ids_error = get_list_of_ids_by_status_and_method(
        "error", method, job_timestamp, db_session
    )
    ids_new = get_list_of_ids_by_status_and_method(
        "new", method, job_timestamp, db_session
    )

    logger.info(f"{method} was done for {ids_done.count()} record(s).")
    logger.info(f"{method} had errors for {ids_error.count()} record(s).")
    logger.info(f"{method} was not handled for {ids_new.count()} record(s).")
