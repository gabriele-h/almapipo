"""
Helper functions for handling csv/tsv inputs. Mostly writing to the dedicated
db-table source_csv and creating a generator for almaids as per first column
of the file.
"""

from datetime import datetime
from logging import getLogger
from typing import Iterable

from sqlalchemy.orm import Session

from alma_rest import db_read_write, input_read

logger = getLogger(__name__)


class CsvHelper:
    """
    Helper Class for CSV-files. Base is a reader with one ordered
    dictionary per line, which is available as a list.
    File existence check is done within alma_rest.input_read.
    :param csv_path: Path to the CSV file to be imported
    :param validation: Check ID structure of first column, default is False
    """

    def __init__(
            self,
            csv_path: str,
            validation: bool = False
    ):
        self.csv_line_list = (
            list(input_read.read_csv_contents(csv_path, validation))
        )

    def extract_almaids(self) -> Iterable[str]:
        """
        Generator of alma_ids as per first column of the csv file.
        :return: Generator of Alma IDs
        """
        for csv_line in self.csv_line_list:
            yield list(csv_line.values())[0]

    def add_to_source_csv_table(
            self,
            job_timestamp: datetime,
            db_session: Session,
    ):
        """
        Imports a whole csv or tsv file to the table source_csv.
        File existence check is done within alma_rest.input_read.
        :param job_timestamp: Timestamp as set in alma_rest.alma_rest
        :param db_session: SQLAlchemy Session
        :return: Generator of Alma IDs
        """
        for csv_line in self.csv_line_list:
            db_read_write.add_csv_line_to_source_csv_table(
                csv_line, job_timestamp, db_session
            )
            
        db_session.commit()
