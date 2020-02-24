""" Read and write to PostgreSQL DB

The PostgreSQL DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, failed, done)
* Store which start time of the job triggered the DB-entry
"""

from os import environ

from sqlalchemy import Column, create_engine, Date, MetaData, select, String, Table

import logfile_setup

# Logfile
logger_read_write_postgres = logfile_setup.create_logger('read_write_postgres')
logfile_setup.log_to_file(logger_read_write_postgres)

# Basic shortenings for SQLAlchemy
metadata = MetaData()


def main():
   engine = setup_db_connection()
   print(type(engine))
   db_job_status_per_id = define_table_job_status_per_id()
   print(engine.connect().execute(select([db_job_status_per_id])))


def setup_db_connection():
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
           Column('status', String()),
           Column('create_date', Date()),
           Column('action', String())
   )
   return table_definition


if __name__=="__main__":
    main()
