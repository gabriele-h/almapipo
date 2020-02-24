""" Read and write to PostgreSQL DB

The PostgreSQL DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, failed, done)
* Store which start time of the job triggered the DB-entry
"""

from os import environ

import sqlalchemy

import logfile_setup

# Logfile
logger_read_write_postgres = logfile_setup.create_logger('read_write_postgres')
logfile_setup.log_to_file(logger_read_write_postgres)

db_user = environ["ALMA_REST_DB_USER"]
db_pw = environ["ALMA_REST_DB_PW"]
db_url = environ["ALMA_REST_DB_URL"]
database = environ["ALMA_REST_DB"]

connection_params = f'postgresql://{db_user}:{db_pw}@{db_url}/{database}'

sql_engine = sqlalchemy.create_engine(connection_params)
