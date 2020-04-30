""" Read and write to DB

The DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, done, error)
* Store which start time of the job triggered the DB-entry
"""

import logging
import connect_db
from datetime import datetime
from typing import OrderedDict

from sqlalchemy import Column, Date, engine, MetaData, select, String, Table

import logfile_setup

# Timestamp for the Script-Run as inserted in the database
job_id = datetime.now()

# Logfile
logger = logging.getLogger(__name__)
logger.info(f"Starting with Job-ID {job_id}")

# Basic shortenings for SQLAlchemy
metadata = MetaData()


def main():
    """
    When used from commandline, the module will test the database
    connection and give according information on stdout.
    :return: None
    """
    logfile_setup.log_to_stdout(logger)
    db_engine = connect_db.setup_db_engine()
    print(type(db_engine))
    db_job_status_per_id = define_table_job_status_per_id()
    print(db_engine.connect().execute(select([db_job_status_per_id])))


def define_table_job_status_per_id() -> Table:
    """
    :return: Definition of the database table job_status_per_id.
    """
    table_definition = Table('job_status_per_id', metadata,
                             Column('alma_id', String()),
                             Column('job_status', String()),
                             Column('job_date', Date()),
                             Column('job_action', String())
                             )
    return table_definition


def define_table_source_csv() -> Table:
    """
    :return: Definition of the database table source_csv.
    """
    table_definition = Table('source_csv', metadata,
                             Column('job_id', Date()),
                             Column('csv_line', JSON)
                             )
    return table_definition


def copy_lines_to_csv_source_table(csv_line: OrderedDict, db_engine: engine):
    """
    For an ordered Dictionary of values retrieved from a csv/tsv file
    create an entry in the database that identifies the job
    responsible for the entry (job_id).
    :param csv_line: Ordered dictionary of values from a line of the input file.
    :param db_engine: database engine as created via connect_db.py
    :return: None
    """
    table_source_csv = define_table_source_csv()
    ins = table_source_csv.insert().values(job_id=job_id, csv_line=csv_line)
    conn = db_engine.connect()
    conn.execute(ins)


if __name__ == "__main__":
    main()
