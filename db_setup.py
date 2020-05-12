"""Setup for DB connection and tables

Does the following two:
* Prepare setup for the DB connection
* Prepare setup of table definitions

DB needs to support native JSON data type, so possible dialects are restricted to the following:
* PostgreSQL
* MySQL >= 5.7
* sqlite >= 3.9
(see https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.JSON)
"""

import logging
from os import environ

# more sqlalchemy setup below with conditions
from sqlalchemy import Column, DateTime, Integer, MetaData, String, Text
from sqlalchemy.ext.declarative import declarative_base

# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = logging.getLogger(__name__)

# Dialect
db_dialect = environ["ALMA_REST_DB_DIALECT"]

if db_dialect == "postgresql":
    from sqlalchemy.dialects.postgresql import JSON
elif db_dialect == "mysql":
    from sqlalchemy.dialects.mysql import JSON
elif db_dialect == "sqlite":
    from sqlalchemy.dialects.sqlite import JSON
else:
    logger.error("No valid db_dialect given.")
    exit(1)

# Basic shortenings for SQLAlchemy
metadata = MetaData()


# Connection setup
def prepare_connection_params_from_env():
    """
    Set up the engine for connections to the PostgreSQL database.
    :return: SQL Engine with connection params as provided via env vars.
    """
    database = environ["ALMA_REST_DB"]
    if db_dialect in ('postgresql', 'mysql'):
        db_user = environ["ALMA_REST_DB_USER"]
        db_pw = environ["ALMA_REST_DB_PW"]
        db_url = environ["ALMA_REST_DB_URL"]
        connection_params = f'{db_dialect}://{db_user}:{db_pw}@{db_url}/{database}'
    elif db_dialect == "sqlite":
        connection_params = f'sqlite:///{database}'
    else:
        logger.error('Connection parameters for the database could not be set. Check env vars.')
    return connection_params


# Table setup
Base = declarative_base()


class JobStatusPerId(Base):
    __tablename__ = 'job_status_per_id'

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime)
    alma_id = Column(String)
    job_status = Column(String)
    job_action = Column(String)


class SourceCsv(Base):
    __tablename__ = 'source_csv'

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime)
    csv_line = Column(JSON)


class FetchedRecords(Base):
    __tablename__ = 'fetched_records'

    primary_key = Column(Integer, primary_key=True)
    job_timestamp = Column(DateTime)
    alma_id = Column(String)
    alma_record = Column(Text)
