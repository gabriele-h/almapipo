"""
Helper functions for handling csv/tsv inputs. Mostly writing to the dedicated
db-table source_csv and creating a generator for almaids as per first column
of the file.
"""

from logging import getLogger
from typing import Iterable

from sqlalchemy.orm import Session

from alma_rest import db_read_write, input_read

logger = getLogger(__name__)


def csv_almaid_generator(
        csv_path: str, validation: bool = False) -> Iterable[str]:
    """
    Generator of alma_ids as per first column of the csv file.
    File existence check is done within alma_rest.input_read.
    :param csv_path: Path to the CSV file to be imported
    :param validation: Check ID structure of first column, defaults to False
    :return: Generator of Alma IDs
    """

    csv_generator = input_read.read_csv_contents(csv_path, validation)

    for csv_line in csv_generator:
        yield list(csv_line.values())[0]


def add_csv_to_source_csv_table(
        csv_path: str,
        job_timestamp: str,
        db_session: Session,
        validation: bool = False
) -> Iterable[str]:
    """
    Imports a whole csv or tsv file to the table source_csv.
    File existence check is done within alma_rest.input_read.
    :param csv_path: Path to the CSV file to be imported
    :param job_timestamp: Timestamp as set in alma_rest.alma_rest
    :param db_session: SQLAlchemy Session
    :param validation: Check ID structure of first column, defaults to False
    :return: Generator of Alma IDs
    """

    csv_generator = input_read.read_csv_contents(csv_path, validation)

    for csv_line in csv_generator:
        db_read_write.add_csv_line_to_source_csv_table(
            csv_line, job_timestamp, db_session
        )
