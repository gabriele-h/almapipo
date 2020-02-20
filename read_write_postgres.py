""" Read and write to PostgreSQL DB

The PostgreSQL DB is intended to do the following:
* Store IDs as fetched from a CSV file
* Store the status of those IDs (new, failed, done)
* Store which start time of the job triggered the DB-entry
"""

from os import environ

import logfile_setup

# Logfile
logger_read_write_postgres = logfile_setup.create_logger('read_write_postgres')
logfile_setup.log_to_file(logger_read_write_postgres)

database = environ["ALMA_REST_DB"]
db_user = environ["ALMA_REST_DB_USER"]
db_pw = environ["ALMA_REST_DB_PW"]
