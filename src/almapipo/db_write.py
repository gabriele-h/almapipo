""" Write to DB

The DB is intended to do the following:
* Store CSV files used for API calls
* Store the status of calls per alma_ids (new, done, error)
* Store which start time of the job triggered the DB-entry
* Store API response contents
* Store data sent to the API
"""

from datetime import datetime
from typing import OrderedDict
from xml.etree.ElementTree import fromstring

from sqlalchemy.orm import Session

from . import setup_db


def update_job_status(status: str,
                      alma_id: str,
                      method: str,
                      job_timestamp: datetime,
                      db_session: Session) -> None:
    """For a given alma_id and job_timestamp update the job_status in
    table job_status_per_id.
    :param status: New status to be set
    :param alma_id: Alma ID to set the status for
    :param method: "DELETE", "GET", "POST" or "PUT"
    :param job_timestamp: Job for which the status should be changed
    :param db_session: Session to be used for the manipulation
    :return: None
    """

    list_of_matched_rows = db_session.query(
        setup_db.JobStatusPerId
    ).filter_by(
        job_timestamp=job_timestamp
    ).filter_by(
        alma_id=alma_id
    ).filter_by(
        job_action=method
    )

    list_of_matched_rows[0].job_status = status


def add_put_post_response(
        alma_id: str,
        record_data: str,
        job_timestamp: datetime,
        db_session: Session) -> None:
    """
    Create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line per Alma record with the data retrieved via Alma API.
    :param alma_id: Alma ID for one specific record.
    :param record_data: Response retrieved via Alma API.
    :param job_timestamp: Identifier of the job causing the DB-entry.
    :param db_session: DB session to add the lines to.
    :return: None
    """

    record_data_xml = fromstring(record_data)

    line_for_table_put_post_responses = setup_db.PutPostResponses(
        alma_id=alma_id,
        alma_record=record_data_xml,
        job_timestamp=job_timestamp,
    )

    db_session.add(line_for_table_put_post_responses)


def add_sent_record(
        alma_id: str,
        record_data: bytes,
        job_timestamp: datetime,
        db_session: Session) -> None:
    """
    Create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line per Alma record with the data to be sent via Alma API.
    :param alma_id: Alma ID for one specific record.
    :param record_data: Record to be sent via Alma API.
    :param job_timestamp: Identifier of the job causing the DB-entry.
    :param db_session: DB session to add the lines to.
    :return: None
    """

    record_data_xml = fromstring(record_data)

    line_for_table_sent_records = setup_db.SentRecords(
        alma_id=alma_id,
        alma_record=record_data_xml,
        job_timestamp=job_timestamp,
    )

    db_session.add(line_for_table_sent_records)


def add_response_content_to_fetched_records(
        alma_id: str,
        record_data,
        job_timestamp: datetime,
        db_session: Session) -> None:
    """
    Create an entry in the database that identifies the job
    responsible for the entry (job_timestamp).
    Adds one line per Alma record with the data retrieved via Alma API.
    :param alma_id: Alma ID for one specific record.
    :param record_data: Record as retrieved via Alma API.
    :param job_timestamp: Identifier of the job causing the DB-entry.
    :param db_session: DB session to add the lines to.
    :return: None
    """

    line_for_table_fetched_records = setup_db.FetchedRecords(
        alma_id=alma_id,
        alma_record=record_data,
        job_timestamp=job_timestamp,
    )

    db_session.add(line_for_table_fetched_records)


def add_csv_line_to_source_csv_table(
        csv_line: OrderedDict,
        job_timestamp: datetime,
        db_session: Session) -> None:
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    Adds one line to source_csv.
    :param csv_line: Ordered dictionary of values from one line from input file
    :param job_timestamp: Timestamp to identify the job which created the line
    :param db_session: DB session to add the data to
    :return: None
    """

    line_for_table_source_csv = setup_db.SourceCsv(
        job_timestamp=job_timestamp,
        csv_line=csv_line
    )

    db_session.add(line_for_table_source_csv)


def add_alma_id_to_job_status_per_id(
        alma_id: str,
        method: str,
        job_timestamp: datetime,
        db_session: Session) -> None:
    """
    For a string of Alma IDs create an entry in job_status_per_id.
    :param alma_id: IDs of the record to be manipulated.
    :param method: GET, PUT, POST or DELETE
    :param job_timestamp: Timestamp to identify the job which created the line.
    :param db_session: DB session to add the data to.
    :return: None
    """

    line_for_table_job_status_per_id = setup_db.JobStatusPerId(
        job_timestamp=job_timestamp,
        alma_id=alma_id,
        job_status="new",
        job_action=method
    )

    db_session.add(line_for_table_job_status_per_id)
