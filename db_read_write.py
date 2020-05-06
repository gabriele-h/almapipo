""" Read and write to DB

The DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, done, error)
* Store which start time of the job triggered the DB-entry
"""

import logging
import db_setup
from datetime import datetime
from typing import OrderedDict

from sqlalchemy import create_engine, engine, select

import logfile_setup

# Timestamp for the Script-Run as inserted in the database
job_id = datetime.now()

# Logfile
logger = logging.getLogger(__name__)
logger.info(f"Starting with Job-ID {job_id}")


def main():
    """
    When used from commandline, the module will test the database
    connection and give according information on stdout.
    :return: None
    """
    logfile_setup.log_to_stdout(logger)

    connection_params = db_setup.prepare_connection_params_from_env()
    db_engine = create_engine(connection_params, echo=True)

    db_engine.connect()


def copy_lines_to_source_csv_table(csv_line: OrderedDict, db_engine: engine):
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    create an entry in the database that identifies the job
    responsible for the entry (job_id).
    :param csv_line: Ordered dictionary of values from a line of the input file.
    :param db_engine: database engine as created via db_setup.py
    :return: None
    """
    table_source_csv = db_setup.TableDefiner.define_source_csv()
    ins = table_source_csv.insert().values(job_id=job_id, csv_line=csv_line)
    conn = db_engine.connect()
    conn.execute(ins)


if __name__ == "__main__":
    main()
