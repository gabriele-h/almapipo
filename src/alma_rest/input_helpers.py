"""
Helper functions for handling csv/tsv inputs. Mostly writing to the dedicated db-table source_csv
and creating a generator for almaids as per first column of the file.
"""

from logging import getLogger
from typing import Iterable

from alma_rest import db_read_write, db_setup, input_read

logger = getLogger(__name__)


def csv_almaid_generator(csv_path: str, validation: bool = False) -> Iterable[str]:
    """
    Generator of alma_ids as per first column of the csv file.
    File existence check is done within alma_rest.input_read.
    :param csv_path: Path to the CSV file to be imported
    :param validation: If set to "False", the first column will not be checked for validity. Defaults to False.
    :return: Generator of Alma IDs
    """

    csv_generator = input_read.read_csv_contents(csv_path, validation)

    for csv_line in csv_generator:
        yield list(csv_line.values())[0]


def add_csv_to_source_csv_table(csv_path: str, job_timestamp: str, validation: bool = False) -> Iterable[str]:
    """
    Imports a whole csv or tsv file to the table source_csv.
    File existence check is done within alma_rest.input_read.
    :param csv_path: Path to the CSV file to be imported
    :param job_timestamp: Timestamp as set in alma_rest.alma_rest
    :param validation: If set to "False", the first column will not be checked for validity. Defaults to False.
    :return: Generator of Alma IDs
    """

    db_session = db_setup.create_db_session()

    csv_generator = input_read.read_csv_contents(csv_path, validation)

    for csv_line in csv_generator:
        db_read_write.add_csv_line_to_source_csv_table(csv_line, job_timestamp, db_session)

    db_session.commit()
    db_session.close()
