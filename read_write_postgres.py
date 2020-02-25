""" Read and write to PostgreSQL DB

The PostgreSQL DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, failed, done)
* Store which start time of the job triggered the DB-entry
"""

import logging
from datetime import datetime
from os import environ

from sqlalchemy import Column, create_engine, Date, MetaData, select, String, Table
from sqlalchemy.dialects.postgresql import JSON, JSONB

import logfile_setup

# Timestamp for the Script-Run as inserted in the database
job_id = datetime.now()

# Logfile
logger = logging.getLogger(__name__)
logger.info(f"Starting with Job-ID {job_id}")

# Basic shortenings for SQLAlchemy
metadata = MetaData()


def main():
   engine = setup_db_engine()
   print(type(engine))
   db_job_status_per_id = define_table_job_status_per_id()
   print(engine.connect().execute(select([db_job_status_per_id])))


def setup_db_engine():
   db_user = environ["ALMA_REST_DB_USER"]
   db_pw = environ["ALMA_REST_DB_PW"]
   db_url = environ["ALMA_REST_DB_URL"]
   database = environ["ALMA_REST_DB"]
   connection_params = f'postgresql://{db_user}:{db_pw}@{db_url}/{database}'
   sql_engine = create_engine(connection_params)
   return sql_engine


def define_table_job_status_per_id() -> Table:
   table_definition = Table('job_status_per_id', metadata,
           Column('alma_id', String()),
           Column('job_status', String()),
           Column('job_date', Date()),
           Column('job_action', String())
   )
   return table_definition


def define_table_source_csv() -> Table:
   table_definition = Table('source_csv', metadata,
           Column('job_id', Date()),
           Column('csv_line', JSON)
   )
   return table_definition


def copy_lines_to_csv_source_table(csv_line, engine):
   """For a CSV-line formatted as an ordered dictionary
   create an entry in the database that identifies the job
   responsible for the entry (job_id)."""
   table_source_csv = define_table_source_csv()
   ins = table_source_csv.insert().values(job_id=job_id, csv_line=csv_line)
   conn = engine.connect()
   result = conn.execute(ins)


if __name__=="__main__":
    main()
