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
from sqlalchemy import Column, Date, MetaData, String, Table

# noinspection PyUnresolvedReferences
import logfile_setup

# Logfile
logger = logging.getLogger(__name__)

# Dialect
db_dialect = environ["ALMA_REST_DB_DIALECT"]

if db_dialect == "postgresql":
    # noinspection PyUnresolvedReferences
    from sqlalchemy.db_dialects.postgresql import JSON
elif db_dialect == "mysql":
    # noinspection PyUnresolvedReferences
    from sqlalchemy.db_dialects.mysql import JSON
elif db_dialect == "sqlite":
    # noinspection PyUnresolvedReferences
    from sqlalchemy.dialects.sqlite import JSON
else:
    logger.error("No valid db_dialect given.")

# Basic shortenings for SQLAlchemy
metadata = MetaData()


def prepare_connection_params_from_env():
    """
    Set up the engine for connections to the PostgreSQL database.
    :return: SQL Engine with connection params as provided via env vars.
    """
    if db_dialect in ('postgresql', 'mysql'):
        db_user = environ["ALMA_REST_DB_USER"]
        db_pw = environ["ALMA_REST_DB_PW"]
        db_url = environ["ALMA_REST_DB_URL"]
    database = environ["ALMA_REST_DB"]
    if db_dialect == "postgresql":
        connection_params = f'postgresql://{db_user}:{db_pw}@{db_url}/{database}'
    elif db_dialect == "mysql":
        connection_params = f'mysql://{db_user}:{db_pw}@{db_url}/{database}'
    elif db_dialect == "sqlite":
        connection_params = f'sqlite:///{database}'
    return connection_params


class TableDefiner:
    """ Definitions of all tables used."""

    @staticmethod
    def define_job_status_per_id() -> Table:
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

    @staticmethod
    def define_source_csv() -> Table:
        """
        :return: Definition of the database table source_csv.
        """
        table_definition = Table('source_csv', metadata,
                                 Column('job_id', Date()),
                                 Column('csv_line', JSON)
                                 )
        return table_definition
